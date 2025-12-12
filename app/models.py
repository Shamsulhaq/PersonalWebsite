"""
Database models for the personal website
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import hashlib
import secrets

from app.database import Base


# Password hashing functions
def hash_password(password: str) -> str:
    """Hash a password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    try:
        salt, pwd_hash = hashed.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
    except:
        return False


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    short_description = Column(String(250))
    description = Column(Text, nullable=False)
    cover_image = Column(String(500))
    technologies = Column(String(500))
    github_url = Column(String(500))
    demo_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    order = Column(Integer, default=0)
    
    images = relationship("ProjectImage", back_populates="project", cascade="all, delete-orphan")


class ProjectImage(Base):
    __tablename__ = "project_images"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    image_path = Column(String(500), nullable=False)
    caption = Column(String(200))
    order = Column(Integer, default=0)
    
    project = relationship("Project", back_populates="images")


class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    excerpt = Column(String(250), nullable=False)
    content = Column(Text, nullable=False)
    cover_image = Column(String(500))
    tags = Column(String(500))
    view_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    images = relationship("BlogImage", back_populates="blog_post", cascade="all, delete-orphan")


class BlogImage(Base):
    __tablename__ = "blog_images"
    
    id = Column(Integer, primary_key=True, index=True)
    blog_post_id = Column(Integer, ForeignKey("blog_posts.id", ondelete="CASCADE"))
    image_path = Column(String(500), nullable=False)
    caption = Column(String(200))
    order = Column(Integer, default=0)
    
    blog_post = relationship("BlogPost", back_populates="images")


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    level = Column(Integer, default=50)
    order = Column(Integer, default=0)


class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return verify_password(password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return hash_password(password)


class SiteProfile(Base):
    __tablename__ = "site_profile"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    title = Column(String(200))
    tagline = Column(String(300))
    bio = Column(Text)
    email = Column(String(200))
    github = Column(String(500))
    linkedin = Column(String(500))
    twitter = Column(String(500))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SiteTheme(Base):
    __tablename__ = "site_theme"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), default="default")
    primary_color = Column(String(20), default="#2563eb")
    secondary_color = Column(String(20), default="#64748b")
    accent_color = Column(String(20), default="#8b5cf6")
    text_primary = Column(String(20), default="#0f172a")
    text_secondary = Column(String(20), default="#475569")
    bg_primary = Column(String(20), default="#ffffff")
    bg_secondary = Column(String(20), default="#f8fafc")
    bg_alt = Column(String(20), default="#f1f5f9")
    hero_bg_type = Column(String(20), default="gradient")
    hero_bg_image = Column(String(500), nullable=True)
    hero_gradient_start = Column(String(20), default="#667eea")
    hero_gradient_end = Column(String(20), default="#764ba2")
    font_family = Column(String(200), default="system")
    border_radius = Column(String(20), default="0.5rem")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContactMessage(Base):
    __tablename__ = "contact_messages"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    subject = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="unread")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Newsletter(Base):
    __tablename__ = "newsletter_subscribers"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True, nullable=False)
    name = Column(String(200))
    status = Column(String(20), default="active")
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    unsubscribed_at = Column(DateTime, nullable=True)


class Resume(Base):
    __tablename__ = "resume"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(300), nullable=False)
    filepath = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
