"""
Admin routes for contact message management
"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import ContactMessage
from app.utils.auth import get_current_admin
from app.utils.helpers import get_profile

router = APIRouter(prefix="/admin/contact")
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
async def admin_contact_messages(
    request: Request,
    status: str = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Admin contact messages list"""
    query = db.query(ContactMessage)
    
    if status and status in ["unread", "read", "archived"]:
        query = query.filter(ContactMessage.status == status)
    
    messages = query.order_by(ContactMessage.created_at.desc()).all()
    
    # Get counts for each status
    counts = {
        "all": db.query(ContactMessage).count(),
        "unread": db.query(ContactMessage).filter(ContactMessage.status == "unread").count(),
        "read": db.query(ContactMessage).filter(ContactMessage.status == "read").count(),
        "archived": db.query(ContactMessage).filter(ContactMessage.status == "archived").count()
    }
    
    return templates.TemplateResponse(
        "admin/contact_messages.html",
        {
            "request": request,
            "admin": current_admin,
            "messages": messages,
            "counts": counts,
            "current_status": status,
            "active_page": "contact"
        }
    )


@router.get("/{message_id}", response_class=HTMLResponse)
async def admin_contact_detail(
    request: Request,
    message_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Admin contact message detail"""
    message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Mark as read if it's unread
    if message.status == "unread":
        message.status = "read"
        db.commit()
    
    return templates.TemplateResponse(
        "admin/contact_detail.html",
        {
            "request": request,
            "admin": current_admin,
            "message": message,
            "active_page": "contact"
        }
    )


@router.post("/{message_id}/mark-read")
async def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Mark contact message as read"""
    message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.status = "read"
    db.commit()
    
    return RedirectResponse(url=f"/admin/contact/{message_id}", status_code=303)


@router.post("/{message_id}/archive")
async def archive_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Archive contact message"""
    message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.status = "archived"
    db.commit()
    
    return RedirectResponse(url=f"/admin/contact/{message_id}", status_code=303)


@router.post("/{message_id}/delete")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete contact message"""
    message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    
    return RedirectResponse(url="/admin/contact", status_code=303)


@router.post("/{message_id}/reply")
async def reply_to_message(
    request: Request,
    message_id: int,
    reply_message: str = Form(...),
    send_copy: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Send reply to contact message via email"""
    from app.utils.email import send_contact_reply
    
    message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Get profile for sender info
    profile = get_profile(db)
    sender_name = profile.name if profile else "Website Admin"
    sender_email = profile.email if profile else current_admin.email
    
    # Send reply email
    success = send_contact_reply(
        to_email=message.email,
        to_name=message.name,
        original_subject=message.subject,
        reply_message=reply_message,
        sender_name=sender_name,
        sender_email=sender_email
    )
    
    if success:
        # Mark as read
        message.status = "read"
        db.commit()
        
        # Optionally send copy to admin
        if send_copy:
            send_contact_reply(
                to_email=sender_email,
                to_name=sender_name,
                original_subject=message.subject,
                reply_message=f"[Copy of reply sent to {message.name}]\n\n{reply_message}",
                sender_name=sender_name,
                sender_email=sender_email
            )
        
        return templates.TemplateResponse(
            "admin/contact_detail.html",
            {
                "request": request,
                "admin": current_admin,
                "message": message,
                "success": True,
                "active_page": "contact"
            }
        )
    else:
        return templates.TemplateResponse(
            "admin/contact_detail.html",
            {
                "request": request,
                "admin": current_admin,
                "message": message,
                "error": "Failed to send email. Please check your email configuration.",
                "active_page": "contact"
            }
        )
