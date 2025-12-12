"""
Admin routes for theme customization
"""
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import SiteTheme
from app.utils.auth import get_current_admin
from app.utils.helpers import save_upload_file

router = APIRouter(prefix="/admin/theme")
templates = Jinja2Templates(directory="templates")

# Theme preset definitions
THEME_PRESETS = {
    "default": {
        "name": "Default Blue",
        "primary_color": "#2563eb",
        "secondary_color": "#64748b",
        "accent_color": "#8b5cf6",
        "text_primary": "#1e293b",
        "text_secondary": "#64748b",
        "bg_primary": "#ffffff",
        "bg_secondary": "#f8fafc",
        "bg_alt": "#f1f5f9",
        "hero_bg_type": "gradient",
        "hero_gradient_start": "#667eea",
        "hero_gradient_end": "#764ba2",
        "font_family": "system-ui, -apple-system, sans-serif",
        "border_radius": "8px"
    },
    "dark": {
        "name": "Dark Mode",
        "primary_color": "#3b82f6",
        "secondary_color": "#6366f1",
        "accent_color": "#8b5cf6",
        "text_primary": "#f1f5f9",
        "text_secondary": "#94a3b8",
        "bg_primary": "#0f172a",
        "bg_secondary": "#1e293b",
        "bg_alt": "#334155",
        "hero_bg_type": "gradient",
        "hero_gradient_start": "#1e3a8a",
        "hero_gradient_end": "#7c3aed",
        "font_family": "system-ui, -apple-system, sans-serif",
        "border_radius": "8px"
    },
    "ocean": {
        "name": "Ocean",
        "primary_color": "#0891b2",
        "secondary_color": "#06b6d4",
        "accent_color": "#22d3ee",
        "text_primary": "#0c4a6e",
        "text_secondary": "#0e7490",
        "bg_primary": "#ecfeff",
        "bg_secondary": "#cffafe",
        "bg_alt": "#a5f3fc",
        "hero_bg_type": "gradient",
        "hero_gradient_start": "#0891b2",
        "hero_gradient_end": "#06b6d4",
        "font_family": "system-ui, -apple-system, sans-serif",
        "border_radius": "12px"
    },
    "sunset": {
        "name": "Sunset",
        "primary_color": "#ea580c",
        "secondary_color": "#f59e0b",
        "accent_color": "#dc2626",
        "text_primary": "#7c2d12",
        "text_secondary": "#c2410c",
        "bg_primary": "#fff7ed",
        "bg_secondary": "#ffedd5",
        "bg_alt": "#fed7aa",
        "hero_bg_type": "gradient",
        "hero_gradient_start": "#f59e0b",
        "hero_gradient_end": "#dc2626",
        "font_family": "system-ui, -apple-system, sans-serif",
        "border_radius": "10px"
    },
    "forest": {
        "name": "Forest",
        "primary_color": "#059669",
        "secondary_color": "#10b981",
        "accent_color": "#34d399",
        "text_primary": "#064e3b",
        "text_secondary": "#047857",
        "bg_primary": "#f0fdf4",
        "bg_secondary": "#dcfce7",
        "bg_alt": "#bbf7d0",
        "hero_bg_type": "gradient",
        "hero_gradient_start": "#059669",
        "hero_gradient_end": "#10b981",
        "font_family": "system-ui, -apple-system, sans-serif",
        "border_radius": "8px"
    },
    "minimal": {
        "name": "Minimal",
        "primary_color": "#18181b",
        "secondary_color": "#52525b",
        "accent_color": "#71717a",
        "text_primary": "#09090b",
        "text_secondary": "#52525b",
        "bg_primary": "#ffffff",
        "bg_secondary": "#fafafa",
        "bg_alt": "#f4f4f5",
        "hero_bg_type": "gradient",
        "hero_gradient_start": "#18181b",
        "hero_gradient_end": "#52525b",
        "font_family": "system-ui, -apple-system, sans-serif",
        "border_radius": "4px"
    }
}


@router.get("", response_class=HTMLResponse)
async def admin_theme(
    request: Request,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Admin theme customization page"""
    theme = db.query(SiteTheme).first()
    if not theme:
        # Create default theme if not exists
        theme = SiteTheme(**THEME_PRESETS["default"])
        db.add(theme)
        db.commit()
        db.refresh(theme)
    
    return templates.TemplateResponse(
        "admin/theme.html",
        {
            "request": request, 
            "admin": current_admin, 
            "theme": theme,
            "presets": THEME_PRESETS,
            "active_page": "theme"
        }
    )


@router.post("/update")
async def admin_theme_update(
    name: str = Form(...),
    primary_color: str = Form(...),
    secondary_color: str = Form(...),
    accent_color: str = Form(...),
    text_primary: str = Form(...),
    text_secondary: str = Form(...),
    bg_primary: str = Form(...),
    bg_secondary: str = Form(...),
    bg_alt: str = Form(...),
    hero_bg_type: str = Form(...),
    hero_gradient_start: str = Form(...),
    hero_gradient_end: str = Form(...),
    font_family: str = Form(...),
    border_radius: str = Form(...),
    hero_bg_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Update theme settings"""
    theme = db.query(SiteTheme).first()
    
    if not theme:
        theme = SiteTheme()
        db.add(theme)
    
    theme.name = name
    theme.primary_color = primary_color
    theme.secondary_color = secondary_color
    theme.accent_color = accent_color
    theme.text_primary = text_primary
    theme.text_secondary = text_secondary
    theme.bg_primary = bg_primary
    theme.bg_secondary = bg_secondary
    theme.bg_alt = bg_alt
    theme.hero_bg_type = hero_bg_type
    theme.hero_gradient_start = hero_gradient_start
    theme.hero_gradient_end = hero_gradient_end
    theme.font_family = font_family
    theme.border_radius = border_radius
    
    # Handle hero background image upload
    if hero_bg_image and hasattr(hero_bg_image, 'filename') and hero_bg_image.filename:
        file_path = save_upload_file(hero_bg_image, "static/uploads/theme")
        theme.hero_bg_image = "/" + file_path
    
    db.commit()
    db.refresh(theme)
    
    return RedirectResponse(url="/admin/theme", status_code=303)


@router.post("/preset/{preset_name}")
async def admin_theme_apply_preset(
    preset_name: str,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Apply a preset theme"""
    if preset_name not in THEME_PRESETS:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    preset = THEME_PRESETS[preset_name]
    theme = db.query(SiteTheme).first()
    
    if not theme:
        theme = SiteTheme()
        db.add(theme)
    
    for key, value in preset.items():
        setattr(theme, key, value)
    
    db.commit()
    
    return RedirectResponse(url="/admin/theme", status_code=303)
