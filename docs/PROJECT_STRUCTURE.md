# Project Reorganization Guide

## New Structure

```
PersonalSite/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection & session
│   ├── models.py            # SQLAlchemy models
│   ├── exceptions.py        # Custom exceptions
│   ├── init_db.py           # Database initialization
│   │
│   ├── routes/              # Route handlers
│   │   ├── __init__.py
│   │   ├── public.py        # Public-facing routes
│   │   ├── admin.py         # Admin panel routes
│   │   └── api.py           # API endpoints
│   │
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── auth.py          # Authentication
│       ├── email.py         # Email utilities
│       ├── helpers.py       # General helpers
│       └── rate_limit.py    # Rate limiting
│
├── static/                  # Static files (CSS, JS, images)
├── templates/               # Jinja2 templates
├── personal_site.db         # SQLite database
├── .env                     # Environment variables
└── requirements.txt         # Python dependencies
```

## Benefits of New Structure

### 1. **Separation of Concerns**
- Routes separated by function (public, admin, API)
- Models in dedicated file
- Utilities organized by purpose
- Configuration centralized

### 2. **Better Maintainability**
- Easier to find specific functionality
- Smaller, focused files
- Clear dependencies
- Better code organization

### 3. **Scalability**
- Easy to add new routes
- Simple to extend functionality
- Clear structure for team collaboration
- Ready for microservices if needed

### 4. **Testing**
- Easier to write unit tests
- Can test components in isolation
- Mock dependencies cleanly

## Migration from Old Structure

### Old Structure Issues:
- `main.py` (1800+ lines) - Too large, hard to navigate
- Mixed concerns in single file
- Utilities scattered
- Hard to test

### Changes Made:

1. **Created `app/` package** - Main application directory
2. **Split `main.py`** - Will be separated into route modules
3. **Moved utilities**:
   - `auth.py` → `app/utils/auth.py`
   - `email_utils.py` → `app/utils/email.py`
   - `exceptions.py` → `app/exceptions.py`

4. **Organized models**:
   - `database.py` models → `app/models.py`
   - Database config → `app/database.py`

5. **Added `app/config.py`** - Centralized configuration

## How to Run

### Development:
```bash
# From project root
uvicorn app.main:app --reload
```

### Production:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Import Changes

### Old:
```python
from database import get_db, Project
from auth import get_current_admin
from email_utils import send_email
```

### New:
```python
from app.database import get_db
from app.models import Project
from app.utils import get_current_admin, send_email
```

## Next Steps

1. **Split routes** - Separate main.py routes into:
   - `app/routes/public.py` - Homepage, projects, blog, contact
   - `app/routes/admin.py` - Admin panel routes
   - `app/routes/api.py` - API endpoints

2. **Update imports** - Update all imports to use new structure

3. **Test** - Ensure all functionality works

4. **Add tests** - Write unit tests for components

5. **Documentation** - Update README with new structure

## Environment Setup

Create `.env` file with:
```env
# Database
DATABASE_URL=sqlite:///./personal_site.db

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=Your Name

# Security
SECRET_KEY=your-secret-key-here
```

## Configuration Options

Edit `app/config.py` for:
- Upload directories
- Pagination settings
- Rate limiting
- Session configuration
- Email settings

## Route Organization Pattern

```python
# app/routes/public.py
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, BlogPost

router = APIRouter()

@router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    # Route logic here
    pass
```

## Testing Structure

```
tests/
├── test_models.py
├── test_routes.py
├── test_auth.py
└── test_email.py
```

## Benefits Achieved

✅ **Clean Code** - Easy to read and understand
✅ **Maintainable** - Simple to update and extend  
✅ **Testable** - Can test components independently
✅ **Scalable** - Ready for growth
✅ **Professional** - Industry-standard structure
