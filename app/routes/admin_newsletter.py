"""
Admin routes for newsletter subscriber management
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Newsletter
from app.utils.auth import get_current_admin

router = APIRouter(prefix="/admin/newsletter")
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
async def admin_newsletter(
    request: Request,
    status: str = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Admin newsletter subscribers list"""
    query = db.query(Newsletter)
    
    if status and status in ["active", "unsubscribed"]:
        query = query.filter(Newsletter.status == status)
    
    subscribers = query.order_by(Newsletter.subscribed_at.desc()).all()
    
    # Get counts
    counts = {
        "all": db.query(Newsletter).count(),
        "active": db.query(Newsletter).filter(Newsletter.status == "active").count(),
        "unsubscribed": db.query(Newsletter).filter(Newsletter.status == "unsubscribed").count()
    }
    
    return templates.TemplateResponse(
        "admin/newsletter.html",
        {
            "request": request,
            "admin": current_admin,
            "subscribers": subscribers,
            "counts": counts,
            "current_status": status,
            "active_page": "newsletter"
        }
    )


@router.post("/{subscriber_id}/delete")
async def delete_subscriber(
    subscriber_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete newsletter subscriber"""
    subscriber = db.query(Newsletter).filter(Newsletter.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    
    db.delete(subscriber)
    db.commit()
    
    return RedirectResponse(url="/admin/newsletter", status_code=303)
