# Personal Website - Complete Setup Guide

## 🎉 What's Been Built

A full-featured personal website with **FastAPI + HTMX + SQLite** featuring:

### Public Site
- Home page with profile information
- Projects showcase with cover images
- Skills display with progress bars
- Blog with posts and cover images
- Responsive, modern design

### Admin Panel (NEW!)
- 🔐 Secure login system with session management
- 👤 Profile management (name, title, bio, social links)
- 📁 Full project CRUD (Create, Read, Update, Delete)
- ✍️ Full blog post CRUD with slug-based URLs
- 🛠️ Skills management by category
- 📸 Image upload for projects and blog posts

## 📦 Installation

### 1. Install Dependencies

Since you're using pipenv:
```bash
pipenv install fastapi==0.109.0 uvicorn[standard]==0.27.0 jinja2==3.1.3 python-multipart==0.0.6 aiofiles==23.2.1 sqlalchemy==2.0.25 pillow==10.2.0 passlib[bcrypt]==1.7.4 python-jose[cryptography]==3.3.0 itsdangerous==2.1.2
```

Or with regular pip:
```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python seed_db.py
```

This will:
- Create all database tables
- Add sample projects, blog posts, and skills
- Create default admin user:
  - **Username:** `admin`
  - **Password:** `admin123`

### 3. Run the Application

```bash
uvicorn main:app --reload
```

Or:
```bash
python main.py
```

### 4. Access Your Site

- **Public Site:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin/login

## 🔑 Admin Panel Usage

### First Login
1. Go to http://localhost:8000/admin/login
2. Login with `admin` / `admin123`
3. **IMPORTANT:** Change your password by creating a new admin user

### Managing Content

#### Edit Profile
- Navigate to **Admin > Profile**
- Update your name, title, tagline, bio
- Add social media links (GitHub, LinkedIn, Twitter)
- Click "Save Changes"

#### Manage Projects
- **View all:** Admin > Projects
- **Add new:** Click "+ New Project" button
- **Edit:** Click "Edit" on any project
- **Delete:** Click "Delete" (with confirmation)

**Project Fields:**
- Title (required)
- Description (required)
- Technologies (comma-separated, e.g., "Python,FastAPI,React")
- GitHub URL (optional)
- Demo URL (optional)
- Order (number for sorting)
- Cover Image (upload)

#### Manage Blog Posts
- **View all:** Admin > Blog
- **Add new:** Click "+ New Post" button
- **Edit:** Click "Edit" on any post
- **Delete:** Click "Delete" (with confirmation)

**Blog Post Fields:**
- Title (required)
- Slug (required, URL-friendly, e.g., "my-first-post")
- Excerpt (required, short description)
- Content (required, supports markdown)
- Tags (comma-separated, e.g., "Python,Tutorial,Web")
- Cover Image (upload)

#### Manage Skills
- **View all:** Admin > Skills
- **Add new:** Click "+ Add Skill"
- **Edit:** Modify inline and click "Save"
- **Delete:** Click "Delete" (with confirmation)

**Skill Fields:**
- Category (e.g., "Backend", "Frontend", "Tools")
- Name (e.g., "Python", "React")
- Level (0-100)
- Order (for sorting within category)

### Creating Additional Admin Users

Run the interactive script:
```bash
python create_admin.py
```

Follow the prompts to create a new admin user with custom username and password.

## 🗂️ Project Structure

```
PersonalSite/
├── main.py                 # FastAPI application with routes
├── database.py             # SQLAlchemy models and database config
├── auth.py                 # Authentication and session management
├── seed_db.py              # Database initialization script
├── create_admin.py         # Script to create admin users
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .gitignore             # Git ignore rules
│
├── templates/
│   ├── base.html          # Base template for public site
│   ├── index.html         # Home page
│   ├── projects.html      # Projects list
│   ├── project_detail.html # Individual project
│   ├── skills.html        # Skills page
│   ├── blog.html          # Blog list
│   ├── blog_post.html     # Individual blog post
│   │
│   ├── partials/
│   │   ├── projects_list.html  # HTMX partial
│   │   └── skills_list.html    # HTMX partial
│   │
│   └── admin/
│       ├── base.html           # Admin base template
│       ├── login.html          # Admin login page
│       ├── dashboard.html      # Admin dashboard
│       ├── profile.html        # Profile editor
│       ├── projects_list.html  # Projects management
│       ├── project_form.html   # Project create/edit
│       ├── blog_list.html      # Blog management
│       ├── blog_form.html      # Blog post create/edit
│       └── skills_list.html    # Skills management
│
├── static/
│   ├── css/
│   │   ├── style.css      # Public site styles
│   │   └── admin.css      # Admin panel styles
│   │
│   └── uploads/           # Uploaded images (auto-created)
│       ├── projects/
│       └── blog/
│
├── data/
│   └── profile.json       # (Legacy, now in database)
│
└── personal_site.db       # SQLite database (auto-created)
```

## 🔒 Security Notes

1. **Change Default Password:** The default admin password is `admin123`. Create a new admin user or change this immediately!

2. **Secret Key:** In `auth.py`, change this line in production:
   ```python
   SECRET_KEY = "your-secret-key-change-this-in-production"
   ```
   Generate a secure key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **HTTPS:** In production, always use HTTPS and set secure cookie flags.

## 📝 Database Schema

### Tables:
- `admin_users` - Admin authentication
- `site_profile` - Site profile information
- `projects` - Project listings
- `project_images` - Project gallery images
- `blog_posts` - Blog posts
- `blog_images` - Blog post images
- `skills` - Skills by category

### Reset Database:
```bash
rm personal_site.db
python seed_db.py
```

## 🚀 Deployment Tips

1. Set environment variables for production
2. Use a production WSGI server (gunicorn)
3. Set up proper logging
4. Configure secure cookies
5. Use a reverse proxy (nginx)
6. Set up SSL/TLS certificates

## 📚 Technology Stack

- **Backend:** FastAPI (Python web framework)
- **Frontend:** HTMX (dynamic interactions without JavaScript)
- **Database:** SQLite (with SQLAlchemy ORM)
- **Templates:** Jinja2
- **Auth:** Session-based with secure password hashing (bcrypt)
- **Styling:** Custom CSS with responsive design

## ❓ Troubleshooting

### "No module named..." errors
Install all dependencies:
```bash
pip install -r requirements.txt
```

### Admin login not working
1. Check database was initialized: `python seed_db.py`
2. Verify username/password
3. Check browser cookies are enabled

### Images not uploading
1. Ensure `static/uploads/` directories exist
2. Check file permissions
3. Verify file size is reasonable

### Port already in use
Change the port:
```bash
uvicorn main:app --reload --port 8001
```

## 🎨 Customization

### Colors
Edit CSS variables in `static/css/style.css`:
```css
:root {
    --primary-color: #2563eb;
    --accent-color: #8b5cf6;
    /* ... */
}
```

### Admin Panel Colors
Edit `static/css/admin.css` for admin-specific styling.

## 📧 Support

For issues or questions:
1. Check the documentation above
2. Review error logs in terminal
3. Verify database initialization
4. Check file permissions

---

**Congratulations!** You now have a fully functional personal website with a complete admin panel for managing all your content! 🎉
