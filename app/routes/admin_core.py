"""
Admin core routes: authentication, dashboard, profile, and settings
"""
from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Project, BlogPost, Skill, ContactMessage, SiteProfile
from app.utils.auth import get_current_admin, authenticate_admin, create_session_token, SESSION_COOKIE_NAME
from app.utils.helpers import get_profile

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request, next: str = None):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {"request": request, "next": next})


@router.post("/login")
async def admin_login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form(None),
    db: Session = Depends(get_db)
):
    """Handle admin login"""
    user = authenticate_admin(username, password, db)
    if not user:
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Invalid username or password", "next": next}
        )
    
    # Create session token
    session_token = create_session_token(user.id)
    
    # Redirect to requested page or dashboard
    redirect_url = next if next and next.startswith("/admin/") else "/admin/dashboard"
    redirect = RedirectResponse(url=redirect_url, status_code=303)
    redirect.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        max_age=86400  # 24 hours
    )
    return redirect


@router.get("/logout")
async def admin_logout():
    """Handle admin logout"""
    redirect = RedirectResponse(url="/admin/login", status_code=303)
    redirect.delete_cookie(SESSION_COOKIE_NAME)
    return redirect


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Admin dashboard with analytics"""
    projects_count = db.query(Project).count()
    blog_posts_count = db.query(BlogPost).count()
    published_posts_count = db.query(BlogPost).filter(BlogPost.is_published == True).count()
    draft_posts_count = blog_posts_count - published_posts_count
    skills_count = db.query(Skill).count()
    unread_messages_count = db.query(ContactMessage).filter(ContactMessage.status == "unread").count()
    
    # Total blog views
    total_views = db.query(func.sum(BlogPost.view_count)).scalar() or 0
    
    # Most viewed posts
    most_viewed = db.query(BlogPost).order_by(BlogPost.view_count.desc()).limit(5).all()
    
    # Recent blog posts
    recent_posts = db.query(BlogPost).order_by(BlogPost.published_at.desc()).limit(5).all()
    
    # Recent contact messages
    recent_messages = db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "admin": current_admin,
            "projects_count": projects_count,
            "blog_posts_count": blog_posts_count,
            "published_posts_count": published_posts_count,
            "draft_posts_count": draft_posts_count,
            "skills_count": skills_count,
            "unread_messages_count": unread_messages_count,
            "total_views": total_views,
            "most_viewed": most_viewed,
            "recent_posts": recent_posts,
            "recent_messages": recent_messages,
            "active_page": "dashboard"
        }
    )


@router.get("/profile", response_class=HTMLResponse)
async def admin_profile_page(
    request: Request,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Admin profile management page"""
    profile = get_profile(db)
    return templates.TemplateResponse(
        "admin/profile.html",
        {"request": request, "admin": current_admin, "profile": profile, "active_page": "profile"}
    )


@router.post("/profile")
async def admin_update_profile(
    request: Request,
    name: str = Form(...),
    title: str = Form(...),
    tagline: str = Form(""),
    bio: str = Form(""),
    email: str = Form(""),
    github: str = Form(""),
    linkedin: str = Form(""),
    twitter: str = Form(""),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Update site profile"""
    profile = db.query(SiteProfile).first()
    if not profile:
        profile = SiteProfile(id=1)
        db.add(profile)
    
    profile.name = name
    profile.title = title
    profile.tagline = tagline
    profile.bio = bio
    profile.email = email
    profile.github = github
    profile.linkedin = linkedin
    profile.twitter = twitter
    
    db.commit()
    
    return RedirectResponse(url="/admin/profile?success=1", status_code=303)


@router.get("/change-password", response_class=HTMLResponse)
async def admin_change_password_page(
    request: Request,
    current_admin = Depends(get_current_admin)
):
    """Change password page"""
    return templates.TemplateResponse(
        "admin/change_password.html",
        {"request": request, "admin": current_admin, "active_page": "settings"}
    )


@router.post("/change-password")
async def admin_change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Change admin password"""
    # Verify current password
    if not current_admin.verify_password(current_password):
        return templates.TemplateResponse(
            "admin/change_password.html",
            {"request": request, "admin": current_admin, "error": "Current password is incorrect", "active_page": "settings"}
        )
    
    # Check if new passwords match
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "admin/change_password.html",
            {"request": request, "admin": current_admin, "error": "New passwords do not match", "active_page": "settings"}
        )
    
    # Check password length
    if len(new_password) < 6:
        return templates.TemplateResponse(
            "admin/change_password.html",
            {"request": request, "admin": current_admin, "error": "Password must be at least 6 characters", "active_page": "settings"}
        )
    
    # Update password
    current_admin.hashed_password = current_admin.hash_password(new_password)
    db.commit()
    
    return RedirectResponse(url="/admin/change-password?success=1", status_code=303)


@router.get("/settings/email", response_class=HTMLResponse)
async def admin_email_settings(
    request: Request,
    success: str = None,
    error: str = None,
    current_admin = Depends(get_current_admin)
):
    """Email settings page"""
    from app.utils import email as email_utils
    
    config = {
        'smtp_server': email_utils.SMTP_SERVER,
        'smtp_port': email_utils.SMTP_PORT,
        'smtp_username': email_utils.SMTP_USERNAME,
        'smtp_password': email_utils.SMTP_PASSWORD,
        'sender_email': email_utils.SENDER_EMAIL,
        'sender_name': email_utils.SENDER_NAME
    }
    
    return templates.TemplateResponse(
        "admin/email_settings.html",
        {
            "request": request,
            "admin": current_admin,
            "config": config,
            "success": success,
            "error": error,
            "active_page": "email"
        }
    )


@router.post("/settings/email/test")
async def test_email_settings(
    test_email: str = Form(...),
    current_admin = Depends(get_current_admin)
):
    """Send test email"""
    from app.utils.email import send_email
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 8px;
            }
            .content {
                background: white;
                padding: 30px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>✓ Email Test Successful!</h2>
        </div>
        <div class="content">
            <p>Congratulations! Your email configuration is working correctly.</p>
            <p>You can now:</p>
            <ul>
                <li>Reply to contact messages</li>
                <li>Send newsletters to subscribers</li>
            </ul>
            <p>This test was sent from your personal website admin panel.</p>
        </div>
    </body>
    </html>
    """
    
    success = send_email(
        to_email=test_email,
        subject="Test Email - Configuration Successful",
        html_content=html_content
    )
    
    if success:
        return RedirectResponse(
            url="/admin/settings/email?success=Test email sent successfully!",
            status_code=303
        )
    else:
        return RedirectResponse(
            url="/admin/settings/email?error=Failed to send test email. Check your configuration.",
            status_code=303
        )
