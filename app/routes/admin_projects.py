"""
Admin routes for project management
"""
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List
import os
from app.database import get_db
from app.models import Project, ProjectImage
from app.utils.auth import get_current_admin
from app.utils.helpers import save_upload_file

router = APIRouter(prefix="/admin/projects")
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
async def admin_projects_list(
    request: Request,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Admin projects list page"""
    projects = db.query(Project).order_by(Project.order).all()
    return templates.TemplateResponse(
        "admin/projects_list.html",
        {"request": request, "admin": current_admin, "projects": projects, "active_page": "projects"}
    )


@router.get("/new", response_class=HTMLResponse)
async def admin_project_new(
    request: Request,
    current_admin = Depends(get_current_admin)
):
    """New project form"""
    return templates.TemplateResponse(
        "admin/project_form.html",
        {"request": request, "admin": current_admin, "project": None, "active_page": "projects"}
    )


@router.post("/new")
async def admin_project_create(
    request: Request,
    title: str = Form(...),
    short_description: str = Form(""),
    description: str = Form(...),
    technologies: str = Form(...),
    github_url: str = Form(""),
    demo_url: str = Form(""),
    order: int = Form(0),
    cover_image: Optional[UploadFile] = File(None),
    gallery_images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create new project"""
    project = Project(
        title=title,
        short_description=short_description,
        description=description,
        technologies=technologies,
        github_url=github_url,
        demo_url=demo_url,
        order=order
    )
    
    if cover_image and cover_image.filename:
        project.cover_image = save_upload_file(cover_image, "static/uploads/projects")
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Handle gallery images
    if gallery_images:
        for idx, img_file in enumerate(gallery_images):
            if img_file and img_file.filename:
                img_path = save_upload_file(img_file, "static/uploads/projects")
                project_image = ProjectImage(
                    project_id=project.id,
                    image_path=img_path,
                    order=idx
                )
                db.add(project_image)
        db.commit()
    
    return RedirectResponse(url="/admin/projects", status_code=303)


@router.get("/{project_id}/edit", response_class=HTMLResponse)
async def admin_project_edit(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Edit project form"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return templates.TemplateResponse(
        "admin/project_form.html",
        {"request": request, "admin": current_admin, "project": project, "active_page": "projects"}
    )


@router.post("/{project_id}/edit")
async def admin_project_update(
    request: Request,
    project_id: int,
    title: str = Form(...),
    short_description: str = Form(""),
    description: str = Form(...),
    technologies: str = Form(...),
    github_url: str = Form(""),
    demo_url: str = Form(""),
    order: int = Form(0),
    cover_image: Optional[UploadFile] = File(None),
    gallery_images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Update project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.title = title
    project.short_description = short_description
    project.description = description
    project.technologies = technologies
    project.github_url = github_url
    project.demo_url = demo_url
    project.order = order
    
    if cover_image and cover_image.filename:
        project.cover_image = save_upload_file(cover_image, "static/uploads/projects")
    
    # Handle new gallery images
    if gallery_images:
        max_order = db.query(ProjectImage).filter(ProjectImage.project_id == project_id).count()
        for idx, img_file in enumerate(gallery_images):
            if img_file and img_file.filename:
                img_path = save_upload_file(img_file, "static/uploads/projects")
                project_image = ProjectImage(
                    project_id=project.id,
                    image_path=img_path,
                    order=max_order + idx
                )
                db.add(project_image)
    
    db.commit()
    
    return RedirectResponse(url="/admin/projects", status_code=303)


@router.get("/{project_id}/images/{image_id}/delete")
async def admin_project_image_delete(
    project_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete project gallery image"""
    image = db.query(ProjectImage).filter(
        ProjectImage.id == image_id,
        ProjectImage.project_id == project_id
    ).first()
    
    if image:
        # Delete file from filesystem
        if image.image_path and os.path.exists(image.image_path):
            try:
                os.remove(image.image_path)
            except:
                pass
        db.delete(image)
        db.commit()
    
    return RedirectResponse(url=f"/admin/projects/{project_id}/edit", status_code=303)


@router.post("/{project_id}/delete")
async def admin_project_delete(
    project_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        # Delete cover image file
        if project.cover_image and os.path.exists(project.cover_image):
            try:
                os.remove(project.cover_image)
            except:
                pass
        
        # Delete all gallery image files
        for image in project.images:
            if image.image_path and os.path.exists(image.image_path):
                try:
                    os.remove(image.image_path)
                except:
                    pass
        
        db.delete(project)
        db.commit()
    
    return RedirectResponse(url="/admin/projects", status_code=303)
