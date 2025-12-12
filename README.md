# Personal Website

A modern, professionally structured personal website built with FastAPI and HTMX to showcase projects, skills, and blog posts.

## Features

### Public Features
- 🏠 Home page with dynamic introduction
- 💼 Projects showcase with image galleries and lightbox
- 🛠️ Skills display with categorization
- 📝 Blog/Thoughts section with rich text content
- 📧 Contact form with email notifications
- 📰 Newsletter subscription system
- 📱 Fully responsive design
- ⚡ Fast and interactive with HTMX

### Admin Features
- 👤 Secure admin panel with authentication
- 📊 Dashboard with DataTables for all lists
- ✏️ Rich text editor (Quill.js) for content
- 📸 Multi-image upload for projects and blog posts
- 📧 Email management (contact replies, newsletter notifications)
- 🎨 Customizable site profile and theme
- 🔐 Password change functionality
- 📄 Resume management
- 🔄 CSRF protection on all forms

## Project Structure

```
PersonalSite/
├── app/                        # Main application package
│   ├── __init__.py
│   ├── config.py               # Centralized configuration
│   ├── database.py             # Database connection & session
│   ├── models.py               # SQLAlchemy models
│   ├── exceptions.py           # Custom exceptions
│   ├── init_db.py              # Database initialization
│   ├── routes/                 # Modular route handlers (80% reduction from main.py)
│   │   ├── __init__.py
│   │   ├── public.py           # Public routes (/, /projects, /blog, /skills, /contact)
│   │   ├── admin_core.py       # Admin auth, dashboard, profile, settings
│   │   ├── admin_projects.py   # Project CRUD with image gallery
│   │   ├── admin_blog.py       # Blog management with newsletter integration
│   │   ├── admin_skills.py     # Skills management
│   │   ├── admin_theme.py      # Theme customization with 6 presets
│   │   ├── admin_contact.py    # Contact message management & email replies
│   │   ├── admin_newsletter.py # Newsletter subscriber management
│   │   └── admin_resume.py     # Resume upload & activation
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── auth.py             # Authentication utilities
│       ├── email.py            # Email functionality (SMTP, templates)
│       ├── helpers.py          # Shared helpers (get_profile, get_theme, save_upload_file)
│       └── rate_limit.py       # Rate limiting for forms & APIs
├── static/                     # Static files (CSS, JS, images)
│   ├── css/
│   └── uploads/                # User uploaded files
│       ├── projects/           # Project images
│       ├── blog/               # Blog images
│       └── resume/             # Resume PDFs
├── templates/                  # Jinja2 templates
│   ├── admin/                  # Admin panel templates
│   ├── errors/                 # Error pages (404, 500)
│   └── partials/               # Reusable HTMX components
├── scripts/                    # Utility scripts
│   ├── create_admin.py         # Create admin users
│   └── seed_db.py              # Database seeding
├── main.py                     # Application entry point (368 lines - 80% reduced!)
├── main_old_backup.py          # Backup of original monolithic file
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── REORGANIZATION_COMPLETE.md  # Code reorganization documentation
└── personal_site.db            # SQLite database (auto-created)
```

## Setup

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd PersonalSite
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or on Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (email, database, secret key)
```

### 5. Initialize Database
```bash
python scripts/seed_db.py
```

This creates a default admin user:
- **Username:** admin
- **Password:** admin123
- ⚠️ **Important:** Change this password immediately after first login!

### 6. Run Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access the Site
- **Public site:** http://localhost:8000
- **Admin panel:** http://localhost:8000/admin/login

## Admin Panel

The admin panel provides comprehensive content management:

### Content Management
- ✏️ **Projects:** Create/edit projects with rich text descriptions and image galleries
- 📝 **Blog Posts:** Write blog posts with Quill rich text editor
- 🛠️ **Skills:** Manage skills organized by categories
- 📄 **Resume:** Upload and manage your resume
- 👤 **Profile:** Edit site profile (name, title, bio, social links)
- 🎨 **Theme:** Customize site colors and appearance

### Communication
- 📧 **Contact Messages:** View and reply to contact form submissions via email
- 📰 **Newsletter:** Manage newsletter subscribers and send notifications
- ⚙️ **Email Settings:** Configure SMTP settings from the dashboard

### Security & Management
- 🔒 **Authentication:** Secure session-based login with CSRF protection
- 🔑 **Password Management:** Change admin password securely
- 📊 **DataTables:** All lists with search, sort, and pagination
- 🚦 **Rate Limiting:** Protection against abuse

### Creating Additional Admin Users
```bash
python scripts/create_admin.py
```

## Database

The application uses **SQLite** with **SQLAlchemy ORM** to store:
- 👤 Admin users with bcrypt password hashing
- 🌐 Site profile and theme customization
- 💼 Projects with galleries and rich text descriptions
- 📝 Blog posts with cover images and rich content
- 🛠️ Skills organized by category
- 📧 Contact messages and newsletter subscriptions
- 📄 Resume files

**Database Management:**
- Auto-creates tables on first run
- Migrations handled by `app/init_db.py`
- To reset: delete `personal_site.db` and run `python scripts/seed_db.py`

## Email Configuration

Configure email in `.env` file:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
```

Or configure from **Admin Panel → Email Settings** after login.

See `docs/EMAIL_SETUP.md` for detailed email configuration guide.

## Development

### Code Structure
The project follows a **clean, modular architecture** (reorganized from 1,897 lines to 368 lines in main.py):

- **`main.py`** (368 lines) - Application entry point with HTMX/API/SEO routes only
- **`app/routes/`** - 10 modular route handlers:
  - `public.py` (225 lines) - All public-facing routes
  - `admin_core.py` (289 lines) - Admin authentication & core features
  - `admin_projects.py` (215 lines) - Project management with galleries
  - `admin_blog.py` (235 lines) - Blog posts with auto-newsletter
  - `admin_skills.py` (95 lines) - Skills CRUD operations
  - `admin_theme.py` (245 lines) - Theme customization (6 presets)
  - `admin_contact.py` (195 lines) - Message management with email replies
  - `admin_newsletter.py` (65 lines) - Subscriber management
  - `admin_resume.py` (125 lines) - Resume upload & activation
- **`app/models.py`** - 12 SQLAlchemy models (Project, BlogPost, Skill, Admin, etc.)
- **`app/database.py`** - Database connection, session, and CSRF token management
- **`app/config.py`** - Centralized environment configuration
- **`app/utils/`** - Utility modules:
  - `helpers.py` - Shared functions (get_profile, get_theme, save_upload_file)
  - `auth.py` - Authentication & session management
  - `email.py` - SMTP email with HTML templates
  - `rate_limit.py` - In-memory rate limiting

### Adding New Features
- **Public routes** → Add to `app/routes/public.py`
- **Admin routes** → Add to appropriate `app/routes/admin_*.py` module
- **API/HTMX endpoints** → Add to `main.py` (keep utility routes centralized)
- **Helper functions** → Add to `app/utils/helpers.py`

### Running Tests
```bash
# Run with pytest when tests are added
pytest
```

### Documentation
- `REORGANIZATION_COMPLETE.md` - Code reorganization summary (1,897 → 368 lines)
- Detailed breakdown of all route modules and their responsibilities
- Migration notes and testing results

## Technologies Used

- **Backend:** FastAPI (Python 3.12+)
- **Database:** SQLite with SQLAlchemy ORM
- **Frontend:** HTMX, Jinja2 templates
- **Rich Text:** Quill.js editor
- **Admin Lists:** DataTables with jQuery
- **Image Gallery:** Custom lightbox with keyboard navigation
- **Authentication:** Session-based with bcrypt password hashing
- **Email:** SMTP with HTML templates
- **Styling:** Custom CSS with responsive design

## License

[Add your license here]

## Contributing

[Add contributing guidelines if open source]
