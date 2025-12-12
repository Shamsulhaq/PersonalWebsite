"""
Utility functions and helpers
"""
from pathlib import Path
import shutil
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models import SiteProfile, SiteTheme


async def save_upload_file(file: UploadFile, destination: str) -> str:
    """Save uploaded file and return the file path"""
    # Generate unique filename
    ext = file.filename.split('.')[-1] if '.' in file.filename else ''
    unique_filename = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())
    
    # Ensure destination directory exists
    Path(destination).mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = Path(destination) / unique_filename
    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Return path with leading slash for web serving
    return "/" + str(file_path).replace("\\", "/")


def get_profile(db: Session):
    """Get site profile from database"""
    profile = db.query(SiteProfile).first()
    if not profile:
        # Return default if not exists
        return type('obj', (object,), {
            "name": "Your Name",
            "title": "Developer",
            "tagline": "Building amazing things",
            "bio": "Welcome to my site",
            "email": "email@example.com",
            "github": "",
            "linkedin": "",
            "twitter": ""
        })()
    return profile


def get_theme(db: Session):
    """Get site theme from database"""
    theme = db.query(SiteTheme).first()
    if not theme:
        # Return default theme
        theme = SiteTheme(
            name="default",
            primary_color="#2563eb",
            secondary_color="#64748b",
            accent_color="#8b5cf6",
            text_primary="#0f172a",
            text_secondary="#475569",
            bg_primary="#ffffff",
            bg_secondary="#f8fafc",
            bg_alt="#f1f5f9",
            hero_bg_type="gradient",
            hero_gradient_start="#667eea",
            hero_gradient_end="#764ba2"
        )
    return theme
