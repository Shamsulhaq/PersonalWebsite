"""
Admin routes for resume management
"""
from fastapi import APIRouter, Request, Depends, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime
import shutil
import os
from app.database import get_db
from app.models import Resume
from app.utils.auth import get_current_admin

router = APIRouter(prefix="/admin/resume")
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
async def admin_resume(
    request: Request,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Admin resume management"""
    resumes = db.query(Resume).order_by(Resume.uploaded_at.desc()).all()
    
    return templates.TemplateResponse(
        "admin/resume.html",
        {
            "request": request,
            "admin": current_admin,
            "resumes": resumes,
            "active_page": "resume"
        }
    )


@router.post("/upload")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Upload new resume"""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Create uploads directory if not exists
    Path("static/uploads/resume").mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    unique_filename = f"resume_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{file_ext}"
    file_path = f"static/uploads/resume/{unique_filename}"
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Deactivate all existing resumes
    db.query(Resume).update({"is_active": False})
    
    # Create new resume record
    resume = Resume(
        filename=file.filename,
        filepath=file_path,
        file_size=file_size,
        is_active=True
    )
    db.add(resume)
    db.commit()
    
    return RedirectResponse(url="/admin/resume", status_code=303)


@router.post("/{resume_id}/activate")
async def activate_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Activate a resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Deactivate all other resumes
    db.query(Resume).update({"is_active": False})
    
    # Activate this one
    resume.is_active = True
    db.commit()
    
    return RedirectResponse(url="/admin/resume", status_code=303)


@router.post("/{resume_id}/delete")
async def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete a resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file
    if os.path.exists(resume.filepath):
        os.remove(resume.filepath)
    
    # Delete record
    db.delete(resume)
    db.commit()
    
    return RedirectResponse(url="/admin/resume", status_code=303)
