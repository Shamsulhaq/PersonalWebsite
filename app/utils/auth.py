from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AdminUser
from app.exceptions import RedirectException
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime, timedelta
from urllib.parse import quote

# Session configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # Change this!
SESSION_COOKIE_NAME = "admin_session"
serializer = URLSafeTimedSerializer(SECRET_KEY)

security = HTTPBasic()

def create_session_token(user_id: int) -> str:
    """Create a session token for the user"""
    return serializer.dumps({"user_id": user_id, "created": datetime.utcnow().isoformat()})

def verify_session_token(token: str, max_age: int = 86400) -> dict:
    """Verify session token (max_age in seconds, default 24 hours)"""
    try:
        data = serializer.loads(token, max_age=max_age)
        return data
    except (SignatureExpired, BadSignature):
        return None

def get_current_admin(request: Request, db: Session = Depends(get_db)) -> AdminUser:
    """Get current authenticated admin user from session"""
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    
    if not session_token:
        # Redirect to login with return URL
        return_url = quote(str(request.url.path))
        raise RedirectException(f"/admin/login?next={return_url}")
    
    session_data = verify_session_token(session_token)
    if not session_data:
        return_url = quote(str(request.url.path))
        raise RedirectException(f"/admin/login?next={return_url}")
    
    user = db.query(AdminUser).filter(
        AdminUser.id == session_data["user_id"],
        AdminUser.is_active == True
    ).first()
    
    if not user:
        return_url = quote(str(request.url.path))
        raise RedirectException(f"/admin/login?next={return_url}")
    
    return user

def authenticate_admin(username: str, password: str, db: Session) -> AdminUser:
    """Authenticate admin user with username and password"""
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    
    if not user or not user.verify_password(password):
        return None
    
    if not user.is_active:
        return None
    
    return user
