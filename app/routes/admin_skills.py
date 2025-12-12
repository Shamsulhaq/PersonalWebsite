"""
Admin routes for skills management
"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Skill
from app.utils.auth import get_current_admin

router = APIRouter(prefix="/admin/skills")
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
async def admin_skills_list(
    request: Request,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Admin skills list page"""
    skills = db.query(Skill).order_by(Skill.category, Skill.order).all()
    
    # Group by category
    skills_by_category = {}
    for skill in skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)
    
    return templates.TemplateResponse(
        "admin/skills_list.html",
        {"request": request, "admin": current_admin, "skills": skills_by_category, "active_page": "skills"}
    )


@router.post("/new")
async def admin_skill_create(
    category: str = Form(...),
    name: str = Form(...),
    level: int = Form(...),
    order: int = Form(0),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create new skill"""
    skill = Skill(
        category=category,
        name=name,
        level=level,
        order=order
    )
    
    db.add(skill)
    db.commit()
    
    return RedirectResponse(url="/admin/skills", status_code=303)


@router.post("/{skill_id}/edit")
async def admin_skill_update(
    skill_id: int,
    category: str = Form(...),
    name: str = Form(...),
    level: int = Form(...),
    order: int = Form(0),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Update skill"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skill.category = category
    skill.name = name
    skill.level = level
    skill.order = order
    
    db.commit()
    
    return RedirectResponse(url="/admin/skills", status_code=303)


@router.post("/{skill_id}/delete")
async def admin_skill_delete(
    skill_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete skill"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if skill:
        db.delete(skill)
        db.commit()
    
    return RedirectResponse(url="/admin/skills", status_code=303)
