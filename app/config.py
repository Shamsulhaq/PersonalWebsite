"""
Application configuration and settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./personal_site.db")

# Upload directories
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
PROJECT_UPLOAD_DIR = UPLOAD_DIR / "projects"
BLOG_UPLOAD_DIR = UPLOAD_DIR / "blog"
RESUME_UPLOAD_DIR = UPLOAD_DIR / "resume"
THEME_UPLOAD_DIR = UPLOAD_DIR / "theme"

# Template and static directories
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USERNAME)
SENDER_NAME = os.getenv("SENDER_NAME", "Personal Site")

# Session configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
SESSION_COOKIE_NAME = "admin_session"

# Security
CSRF_TOKEN_MAX_AGE = 3600  # 1 hour

# Rate limiting
RATE_LIMIT_REQUESTS = 5
RATE_LIMIT_WINDOW = 60  # seconds

# Pagination
ITEMS_PER_PAGE_PROJECTS = 9
ITEMS_PER_PAGE_BLOG = 10

# Create upload directories if they don't exist
for directory in [PROJECT_UPLOAD_DIR, BLOG_UPLOAD_DIR, RESUME_UPLOAD_DIR, THEME_UPLOAD_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
