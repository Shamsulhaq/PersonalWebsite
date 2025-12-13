"""
Public-facing routes for the personal website
"""
import os
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from app.database import get_db, generate_csrf_token, verify_csrf_token
from app.models import Project, BlogPost, Skill, ContactMessage, Resume
from app.utils.helpers import get_profile, get_theme
from app.utils.rate_limit import check_rate_limit

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page"""
    profile = get_profile(db)
    theme = get_theme(db)
    # Get latest 4 projects
    projects = db.query(Project).order_by(Project.order).limit(4).all()
    # Check if resume exists
    has_resume = db.query(Resume).filter(Resume.is_active == True).first() is not None
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "profile": profile, "theme": theme, "projects": projects, "active_page": "home", "has_resume": has_resume}
    )


@router.get("/projects", response_class=HTMLResponse)
async def projects(request: Request, page: int = 1, db: Session = Depends(get_db)):
    """Projects showcase page with pagination"""
    per_page = 9
    offset = (page - 1) * per_page
    
    total_projects = db.query(Project).count()
    total_pages = (total_projects + per_page - 1) // per_page
    
    projects = db.query(Project).options(joinedload(Project.images)).order_by(Project.order).offset(offset).limit(per_page).all()
    
    # Fix image paths if they don't start with /
    for project in projects:
        if project.cover_image and not project.cover_image.startswith('/'):
            project.cover_image = '/' + project.cover_image
        for img in project.images:
            if img.image_path and not img.image_path.startswith('/'):
                img.image_path = '/' + img.image_path
    
    profile = get_profile(db)
    theme = get_theme(db)
    return templates.TemplateResponse(
        "projects.html",
        {"request": request, "projects": projects, "profile": profile, "theme": theme, "active_page": "projects", "page": page, "total_pages": total_pages}
    )


@router.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(request: Request, project_id: int, db: Session = Depends(get_db)):
    """Individual project detail page"""
    project = db.query(Project).options(joinedload(Project.images)).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Fix image paths if they don't start with /
    if project.cover_image and not project.cover_image.startswith('/'):
        project.cover_image = '/' + project.cover_image
    
    for img in project.images:
        if img.image_path and not img.image_path.startswith('/'):
            img.image_path = '/' + img.image_path
    
    profile = get_profile(db)
    theme = get_theme(db)
    return templates.TemplateResponse(
        "project_detail.html",
        {"request": request, "project": project, "profile": profile, "theme": theme, "active_page": "projects"}
    )


@router.get("/skills", response_class=HTMLResponse)
async def skills(request: Request, db: Session = Depends(get_db)):
    """Skills page"""
    skills = db.query(Skill).order_by(Skill.category, Skill.order).all()
    
    # Group skills by category
    skills_by_category = {}
    for skill in skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)
    
    profile = get_profile(db)
    theme = get_theme(db)
    return templates.TemplateResponse(
        "skills.html",
        {"request": request, "skills": skills_by_category, "profile": profile, "theme": theme, "active_page": "skills"}
    )


@router.get("/blog", response_class=HTMLResponse)
async def blog(request: Request, page: int = 1, search: str = None, db: Session = Depends(get_db)):
    """Blog/thoughts page with search and pagination"""
    per_page = 10
    offset = (page - 1) * per_page
    
    query = db.query(BlogPost).filter(BlogPost.is_published == True)
    
    # Search functionality
    if search:
        query = query.filter(
            (BlogPost.title.contains(search)) | 
            (BlogPost.excerpt.contains(search)) | 
            (BlogPost.content.contains(search)) |
            (BlogPost.tags.contains(search))
        )
    
    total_posts = query.count()
    total_pages = (total_posts + per_page - 1) // per_page
    
    posts = query.order_by(BlogPost.published_at.desc()).offset(offset).limit(per_page).all()
    
    profile = get_profile(db)
    theme = get_theme(db)
    return templates.TemplateResponse(
        "blog.html",
        {
            "request": request, 
            "posts": posts, 
            "profile": profile, 
            "theme": theme, 
            "active_page": "blog",
            "page": page,
            "total_pages": total_pages,
            "search": search
        }
    )


@router.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(request: Request, slug: str, db: Session = Depends(get_db)):
    """Individual blog post"""
    post = db.query(BlogPost).filter(BlogPost.slug == slug, BlogPost.is_published == True).first()
    
    related_posts = []
    if post:
        # Increment view count
        post.view_count += 1
        db.commit()
        
        # Find related posts by matching tags
        if post.tags:
            post_tags = set(tag.strip().lower() for tag in post.tags.split(','))
            all_posts = db.query(BlogPost).filter(
                BlogPost.is_published == True,
                BlogPost.id != post.id
            ).all()
            
            # Calculate relevance score
            scored_posts = []
            for other_post in all_posts:
                if other_post.tags:
                    other_tags = set(tag.strip().lower() for tag in other_post.tags.split(','))
                    common_tags = post_tags.intersection(other_tags)
                    if common_tags:
                        scored_posts.append((len(common_tags), other_post))
            
            # Sort by relevance and get top 3
            scored_posts.sort(reverse=True, key=lambda x: x[0])
            related_posts = [p[1] for p in scored_posts[:3]]
    
    profile = get_profile(db)
    theme = get_theme(db)
    return templates.TemplateResponse(
        "blog_post.html",
        {"request": request, "post": post, "related_posts": related_posts, "profile": profile, "theme": theme, "active_page": "blog"}
    )


@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request, success: bool = False, error: str = None, db: Session = Depends(get_db)):
    """Contact page"""
    profile = get_profile(db)
    theme = get_theme(db)
    csrf_token = generate_csrf_token()
    return templates.TemplateResponse(
        "contact.html",
        {"request": request, "profile": profile, "theme": theme, "active_page": "contact", 
         "success": success, "error": error, "csrf_token": csrf_token}
    )


@router.post("/contact")
async def contact_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle contact form submission with CSRF protection and rate limiting"""
    # Verify CSRF token
    if not verify_csrf_token(csrf_token):
        return RedirectResponse(url="/contact?error=Invalid+security+token", status_code=303)
    
    # Check rate limit
    client_ip = request.client.host
    if not check_rate_limit(client_ip, limit=3, window=60):
        return RedirectResponse(url="/contact?error=Too+many+requests.+Please+try+again+later.", status_code=303)
    
    try:
        contact_msg = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message,
            status="unread"
        )
        db.add(contact_msg)
        db.commit()
        return RedirectResponse(url="/contact?success=1", status_code=303)
    except Exception as e:
        return RedirectResponse(url="/contact?error=Failed+to+send+message", status_code=303)


@router.get("/newsletter/unsubscribe", response_class=HTMLResponse)
async def newsletter_unsubscribe_page(request: Request, email: str = None, db: Session = Depends(get_db)):
    """Newsletter unsubscribe page"""
    from app.models import Newsletter
    
    profile = get_profile(db)
    theme = get_theme(db)
    
    # Check if email is already unsubscribed or not found
    subscriber = None
    if email:
        subscriber = db.query(Newsletter).filter(Newsletter.email == email).first()
    
    csrf_token = generate_csrf_token()
    
    return templates.TemplateResponse(
        "newsletter_unsubscribe.html",
        {
            "request": request, 
            "profile": profile, 
            "theme": theme, 
            "email": email,
            "subscriber": subscriber,
            "csrf_token": csrf_token
        }
    )


@router.post("/newsletter/unsubscribe", response_class=HTMLResponse)
async def newsletter_unsubscribe_submit(
    request: Request,
    email: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process newsletter unsubscription"""
    from app.models import Newsletter
    from datetime import datetime
    
    if not verify_csrf_token(csrf_token):
        return RedirectResponse(url="/newsletter/unsubscribe?error=Invalid+security+token", status_code=303)
    
    try:
        subscriber = db.query(Newsletter).filter(Newsletter.email == email).first()
        if subscriber and subscriber.status == "active":
            subscriber.status = "unsubscribed"
            subscriber.unsubscribed_at = datetime.utcnow()
            db.commit()
            return RedirectResponse(url="/newsletter/unsubscribe?success=1", status_code=303)
        elif subscriber and subscriber.status == "unsubscribed":
            return RedirectResponse(url="/newsletter/unsubscribe?already=1", status_code=303)
        else:
            return RedirectResponse(url="/newsletter/unsubscribe?notfound=1", status_code=303)
    except Exception as e:
        db.rollback()
        return RedirectResponse(url="/newsletter/unsubscribe?error=Failed+to+unsubscribe", status_code=303)
