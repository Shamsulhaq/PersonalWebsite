"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import secrets
from itsdangerous import URLSafeTimedSerializer

DATABASE_URL = "sqlite:///./personal_site.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# CSRF protection
SECRET_KEY = secrets.token_hex(32)
csrf_serializer = URLSafeTimedSerializer(SECRET_KEY)

def get_db():
    """Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_csrf_token() -> str:
    """Generate a CSRF token"""
    return csrf_serializer.dumps(secrets.token_hex(16))

def verify_csrf_token(token: str, max_age: int = 3600) -> bool:
    """Verify a CSRF token (valid for 1 hour by default)"""
    try:
        csrf_serializer.loads(token, max_age=max_age)
        return True
    except:
        return False
