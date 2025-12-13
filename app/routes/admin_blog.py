"""
Admin routes for blog post management
"""
import os
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models import BlogPost, Newsletter
from app.utils.auth import get_current_admin
from app.utils.helpers import get_profile, save_upload_file

router = APIRouter(prefix="/admin/blog")
templates = Jinja2Templates(directory="templates")
SITE_URL = os.getenv("SITE_URL", "https://shamsul.me")

@router.get("", response_class=HTMLResponse)
async def admin_blog_list(
    request: Request,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Admin blog posts list page"""
    posts = db.query(BlogPost).order_by(BlogPost.published_at.desc()).all()
    return templates.TemplateResponse(
        "admin/blog_list.html",
        {"request": request, "admin": current_admin, "posts": posts, "active_page": "blog"}
    )


@router.get("/new", response_class=HTMLResponse)
async def admin_blog_new(
    request: Request,
    current_admin = Depends(get_current_admin)
):
    """New blog post form"""
    return templates.TemplateResponse(
        "admin/blog_form.html",
        {"request": request, "admin": current_admin, "post": None, "active_page": "blog"}
    )


@router.post("/new")
async def admin_blog_create(
    request: Request,
    title: str = Form(...),
    slug: str = Form(...),
    excerpt: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    is_published: Optional[str] = Form(None),
    cover_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create new blog post"""
    # Check if slug already exists
    existing = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    if existing:
        post = None
        return templates.TemplateResponse(
            "admin/blog_form.html",
            {"request": request, "admin": current_admin, "post": post, "error": "Slug already exists", "active_page": "blog"}
        )
    
    post = BlogPost(
        title=title,
        slug=slug,
        excerpt=excerpt,
        content=content,
        tags=tags,
        is_published=bool(is_published)
    )
    
    if cover_image and cover_image.filename:
        post.cover_image = await save_upload_file(cover_image, "static/uploads/blog")
    
    db.add(post)
    db.commit()
    
    # Send newsletter if post is published
    if bool(is_published):
        from app.utils.email import send_newsletter_notification
        
        # Get active subscribers
        subscribers = db.query(Newsletter).filter(Newsletter.status == "active").all()
        if subscribers:
            profile = get_profile(db)
            site_url = SITE_URL
            sender_name = profile.name if profile else "Blog Admin"
            
            subscriber_list = [{'email': s.email, 'name': s.name or 'there'} for s in subscribers]
            
            # Send in background (non-blocking)
            import threading
            thread = threading.Thread(
                target=send_newsletter_notification,
                args=(subscriber_list, title, excerpt, slug, site_url, sender_name)
            )
            thread.start()
    
    return RedirectResponse(url="/admin/blog", status_code=303)


@router.get("/{post_id}/edit", response_class=HTMLResponse)
async def admin_blog_edit(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Edit blog post form"""
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return templates.TemplateResponse(
        "admin/blog_form.html",
        {"request": request, "admin": current_admin, "post": post, "active_page": "blog"}
    )


@router.post("/{post_id}/edit")
async def admin_blog_update(
    request: Request,
    post_id: int,
    title: str = Form(...),
    slug: str = Form(...),
    excerpt: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    is_published: Optional[str] = Form(None),
    cover_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Update blog post"""
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    # Check if slug changed and already exists
    if post.slug != slug:
        existing = db.query(BlogPost).filter(BlogPost.slug == slug).first()
        if existing:
            return templates.TemplateResponse(
                "admin/blog_form.html",
                {"request": request, "admin": current_admin, "post": post, "error": "Slug already exists", "active_page": "blog"}
            )
    
    # Check if post is being published for the first time
    was_draft = not post.is_published
    
    post.title = title
    post.slug = slug
    post.excerpt = excerpt
    post.content = content
    post.tags = tags
    post.is_published = bool(is_published)
    post.updated_at = datetime.utcnow()
    
    if cover_image and cover_image.filename:
        post.cover_image = await save_upload_file(cover_image, "static/uploads/blog")
    
    db.commit()
    
    # Send newsletter if post is being published for first time
    if was_draft and bool(is_published):
        from app.utils.email import send_newsletter_notification
        
        # Get active subscribers
        subscribers = db.query(Newsletter).filter(Newsletter.status == "active").all()
        if subscribers:
            profile = get_profile(db)
            site_url = SITE_URL
            sender_name = profile.name if profile else "Blog Admin"
            
            subscriber_list = [{'email': s.email, 'name': s.name or 'there'} for s in subscribers]
            
            # Send in background (non-blocking)
            import threading
            thread = threading.Thread(
                target=send_newsletter_notification,
                args=(subscriber_list, title, excerpt, slug, site_url, sender_name)
            )
            thread.start()
    
    return RedirectResponse(url="/admin/blog", status_code=303)


@router.post("/{post_id}/delete")
async def admin_blog_delete(
    post_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete blog post"""
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if post:
        # Delete cover image file
        if post.cover_image:
            import os
            if os.path.exists(post.cover_image):
                try:
                    os.remove(post.cover_image)
                except:
                    pass
        
        db.delete(post)
        db.commit()
    
    return RedirectResponse(url="/admin/blog", status_code=303)
