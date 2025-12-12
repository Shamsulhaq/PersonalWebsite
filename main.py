from fastapi import FastAPI, Request, Depends, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db, generate_csrf_token, verify_csrf_token
from app.models import Project, BlogPost, Skill, ProjectImage, BlogImage, SiteProfile, SiteTheme, ContactMessage, Newsletter, Resume
from app.init_db import init_db
from app.utils.auth import get_current_admin, authenticate_admin, create_session_token, SESSION_COOKIE_NAME
from app.exceptions import RedirectException
from typing import Optional, List, Dict
import json
from pathlib import Path
import shutil
import uuid
from datetime import datetime, timedelta
from urllib.parse import quote
import os

app = FastAPI(title="Personal Website")

# Rate limiting - simple in-memory store
rate_limit_store: Dict[str, list] = {}

def check_rate_limit(client_ip: str, limit: int = 5, window: int = 60) -> bool:
    """Check if client has exceeded rate limit (limit requests per window seconds)"""
    now = datetime.utcnow()
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Clean old requests outside window
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if (now - req_time).total_seconds() < window
    ]
    
    # Check if limit exceeded
    if len(rate_limit_store[client_ip]) >= limit:
        return False
    
    # Add current request
    rate_limit_store[client_ip].append(now)
    return True

# Exception handler for redirect
@app.exception_handler(RedirectException)
async def redirect_exception_handler(request: Request, exc: RedirectException):
    return RedirectResponse(url=exc.url, status_code=303)

# Custom error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    from app.utils.helpers import get_profile, get_theme
    db = next(get_db())
    profile = get_profile(db)
    theme = get_theme(db)
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request, "profile": profile, "theme": theme},
        status_code=404
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    from app.utils.helpers import get_profile, get_theme
    db = next(get_db())
    profile = get_profile(db)
    theme = get_theme(db)
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request, "profile": profile, "theme": theme},
        status_code=500
    )

# Initialize database with auto-migration on startup
@app.on_event("startup")
async def startup_event():
    """Run database initialization and migrations on server startup"""
    init_db()
    print("✓ Database initialized with auto-migrations")

# Create upload directories
Path("static/uploads/projects").mkdir(parents=True, exist_ok=True)
Path("static/uploads/blog").mkdir(parents=True, exist_ok=True)
Path("static/uploads/resume").mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Import helper functions
from app.utils.helpers import get_profile, get_theme, save_upload_file

# Import routers
from app.routes.public import router as public_router
from app.routes.admin_core import router as admin_core_router
from app.routes.admin_projects import router as admin_projects_router
from app.routes.admin_blog import router as admin_blog_router
from app.routes.admin_skills import router as admin_skills_router
from app.routes.admin_theme import router as admin_theme_router
from app.routes.admin_contact import router as admin_contact_router
from app.routes.admin_newsletter import router as admin_newsletter_router
from app.routes.admin_resume import router as admin_resume_router

# Include routers
app.include_router(public_router)
app.include_router(admin_core_router)
app.include_router(admin_projects_router)
app.include_router(admin_blog_router)
app.include_router(admin_skills_router)
app.include_router(admin_theme_router)
app.include_router(admin_contact_router)
app.include_router(admin_newsletter_router)
app.include_router(admin_resume_router)

# ==================== HTMX & API ROUTES ====================

# HTMX partial endpoints
@app.get("/api/projects", response_class=HTMLResponse)
async def get_projects_partial(request: Request, db: Session = Depends(get_db)):
    """Return projects partial for HTMX"""
    from sqlalchemy.orm import joinedload
    projects = db.query(Project).options(joinedload(Project.images)).order_by(Project.order).limit(3).all()
    
    # Fix image paths if they don't start with /
    for project in projects:
        if project.cover_image and not project.cover_image.startswith('/'):
            project.cover_image = '/' + project.cover_image
        for img in project.images:
            if not img.image_path.startswith('/'):
                img.image_path = '/' + img.image_path
    
    profile = get_profile(db)
    return templates.TemplateResponse(
        "partials/projects_list.html",
        {"request": request, "projects": projects, "profile": profile}
    )

# Image upload handlers for TinyMCE
@app.post("/api/upload/project-image")
async def upload_project_image(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    caption: str = Form(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Upload project image"""
    # Validate file type
    if not file.content_type.startswith("image/"):
        return {"success": False, "message": "Only image files are allowed"}
    
    # Save file
    image_path = await save_upload_file(file, "static/uploads/projects")
    
    # Add to database if project_id provided
    if project_id:
        project_image = ProjectImage(
            project_id=project_id,
            image_path=image_path,
            caption=caption or ""
        )
        db.add(project_image)
        db.commit()
    
    return {"success": True, "image_path": image_path}

@app.post("/api/upload/blog-image")
async def upload_blog_image(
    file: UploadFile = File(...),
    blog_id: int = Form(None),
    caption: str = Form(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Upload blog image"""
    # Validate file type
    if not file.content_type.startswith("image/"):
        return {"success": False, "message": "Only image files are allowed"}
    
    # Save file
    image_path = await save_upload_file(file, "static/uploads/blog")
    
    # Add to database if blog_id provided
    if blog_id:
        blog_image = BlogImage(
            blog_post_id=blog_id,
            image_path=image_path,
            caption=caption or ""
        )
        db.add(blog_image)
        db.commit()
    
    return {"success": True, "image_path": image_path}

# CSRF Token endpoint
@app.get("/api/csrf-token")
async def get_csrf_token():
    """Get a CSRF token for forms"""
    return JSONResponse({"token": generate_csrf_token()})

# Newsletter subscription
@app.post("/api/newsletter/subscribe")
async def newsletter_subscribe(
    request: Request,
    email: str = Form(...),
    name: str = Form(None),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Subscribe to newsletter"""
    # Verify CSRF token
    if not verify_csrf_token(csrf_token):
        return JSONResponse({"success": False, "message": "Invalid security token"})
    
    # Check rate limit
    client_ip = request.client.host
    if not check_rate_limit(client_ip, limit=3, window=60):
        return JSONResponse({"success": False, "message": "Too many requests. Please try again later."})
    
    try:
        # Check if already subscribed
        existing = db.query(Newsletter).filter(Newsletter.email == email).first()
        if existing:
            if existing.status == "active":
                return JSONResponse({"success": False, "message": "This email is already subscribed"})
            else:
                # Reactivate subscription
                existing.status = "active"
                existing.subscribed_at = datetime.utcnow()
                existing.unsubscribed_at = None
                db.commit()
                return JSONResponse({"success": True, "message": "Welcome back! You've been resubscribed."})
        
        # Create new subscription
        subscriber = Newsletter(email=email, name=name, status="active")
        db.add(subscriber)
        db.commit()
        return JSONResponse({"success": True, "message": "Thank you for subscribing!"})
    except Exception as e:
        db.rollback()
        return JSONResponse({"success": False, "message": "Failed to subscribe. Please try again."})

@app.post("/api/newsletter/unsubscribe")
async def newsletter_unsubscribe(
    email: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Unsubscribe from newsletter"""
    if not verify_csrf_token(csrf_token):
        return JSONResponse({"success": False, "message": "Invalid security token"})
    
    try:
        subscriber = db.query(Newsletter).filter(Newsletter.email == email).first()
        if subscriber and subscriber.status == "active":
            subscriber.status = "unsubscribed"
            subscriber.unsubscribed_at = datetime.utcnow()
            db.commit()
            return JSONResponse({"success": True, "message": "You've been unsubscribed."})
        return JSONResponse({"success": False, "message": "Email not found or already unsubscribed"})
    except Exception as e:
        db.rollback()
        return JSONResponse({"success": False, "message": "Failed to unsubscribe"})

# Resume download
@app.get("/download/resume")
async def download_resume(db: Session = Depends(get_db)):
    """Download the active resume"""
    resume = db.query(Resume).filter(Resume.is_active == True).order_by(Resume.uploaded_at.desc()).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if not os.path.exists(resume.filepath):
        raise HTTPException(status_code=404, detail="Resume file not found")
    
    return FileResponse(
        path=resume.filepath,
        filename=resume.filename,
        media_type="application/pdf"
    )

# SEO Routes
@app.get("/robots.txt", response_class=Response)
async def robots():
    """Generate robots.txt"""
    content = """User-agent: *
Allow: /
Disallow: /admin/
Sitemap: /sitemap.xml"""
    return Response(content=content, media_type="text/plain")

@app.get("/sitemap.xml", response_class=Response)
async def sitemap(request: Request, db: Session = Depends(get_db)):
    """Generate sitemap.xml"""
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    
    # Get all published blog posts
    posts = db.query(BlogPost).filter(BlogPost.is_published == True).all()
    projects = db.query(Project).all()
    
    urls = []
    # Homepage
    urls.append(f'<url><loc>{base_url}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>')
    
    # Projects
    urls.append(f'<url><loc>{base_url}/projects</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>')
    for project in projects:
        urls.append(f'<url><loc>{base_url}/projects/{project.id}</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>')
    
    # Skills
    urls.append(f'<url><loc>{base_url}/skills</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>')
    
    # Blog
    urls.append(f'<url><loc>{base_url}/blog</loc><changefreq>daily</changefreq><priority>0.9</priority></url>')
    for post in posts:
        urls.append(f'<url><loc>{base_url}/blog/{post.slug}</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>')
    
    # Contact
    urls.append(f'<url><loc>{base_url}/contact</loc><changefreq>yearly</changefreq><priority>0.6</priority></url>')
    
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {''.join(urls)}
</urlset>'''
    
    return Response(content=sitemap, media_type="application/xml")

@app.get("/rss.xml", response_class=Response)
async def rss(request: Request, db: Session = Depends(get_db)):
    """Generate RSS feed for blog"""
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    profile = get_profile(db)
    
    # Get latest 20 published posts
    posts = db.query(BlogPost).filter(BlogPost.is_published == True).order_by(BlogPost.published_at.desc()).limit(20).all()
    
    items = []
    for post in posts:
        items.append(f'''
        <item>
            <title>{post.title}</title>
            <link>{base_url}/blog/{post.slug}</link>
            <description>{post.excerpt}</description>
            <pubDate>{post.published_at.strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>
            <guid>{base_url}/blog/{post.slug}</guid>
        </item>''')
    
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>{profile.name if profile else "Personal Blog"}</title>
        <link>{base_url}</link>
        <description>{profile.tagline if profile else "Personal blog and thoughts"}</description>
        <language>en-us</language>
        <lastBuildDate>{datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
        {''.join(items)}
    </channel>
</rss>'''
    
    return Response(content=rss, media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
