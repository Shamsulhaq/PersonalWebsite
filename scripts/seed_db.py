from database import SessionLocal, Project, BlogPost, Skill, ProjectImage, BlogImage, AdminUser, SiteProfile, SiteTheme, init_db
from datetime import datetime

def seed_database():
    """Populate database with sample data"""
    # Initialize database
    init_db()
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(ProjectImage).delete()
        db.query(BlogImage).delete()
        db.query(Project).delete()
        db.query(BlogPost).delete()
        db.query(Skill).delete()
        db.query(SiteProfile).delete()
        # Don't delete AdminUser to preserve login credentials
        
        # Create default admin user if not exists
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            admin = AdminUser(
                username="admin",
                email="admin@example.com",
                hashed_password=AdminUser.hash_password("admin123")  # Change this password!
            )
            db.add(admin)
            db.commit()
            print("✅ Default admin user created (username: admin, password: admin123)")
        
        # Create site profile
        profile = SiteProfile(
            id=1,
            name="Your Name",
            title="Full Stack Developer",
            tagline="Building elegant solutions to complex problems",
            bio="I'm a passionate developer with expertise in web technologies, backend systems, and modern frameworks. I love creating efficient, scalable applications that make a difference.",
            email="your.email@example.com",
            github="https://github.com/yourusername",
            linkedin="https://linkedin.com/in/yourusername",
            twitter="https://twitter.com/yourusername"
        )
        db.add(profile)
        db.commit()
        
        # Create default theme if not exists
        theme = db.query(SiteTheme).first()
        if not theme:
            theme = SiteTheme(
                id=1,
                name="default",
                primary_color="#2563eb",
                secondary_color="#64748b",
                accent_color="#8b5cf6",
                hero_gradient_start="#667eea",
                hero_gradient_end="#764ba2"
            )
            db.add(theme)
            db.commit()
        
        # Add Projects
        projects = [
            Project(
                title="E-Commerce Platform",
                description="A full-featured e-commerce platform with payment integration, inventory management, and real-time analytics.",
                cover_image="/static/uploads/projects/ecommerce-cover.jpg",
                technologies="Python,FastAPI,PostgreSQL,React",
                github_url="https://github.com/yourusername/ecommerce",
                demo_url="https://demo.example.com",
                order=1
            ),
            Project(
                title="Task Management App",
                description="Collaborative task management application with real-time updates using WebSockets.",
                cover_image="/static/uploads/projects/taskmanager-cover.jpg",
                technologies="Node.js,Express,MongoDB,Socket.io",
                github_url="https://github.com/yourusername/taskmanager",
                demo_url="https://tasks.example.com",
                order=2
            ),
            Project(
                title="Weather Dashboard",
                description="Interactive weather dashboard with data visualization and forecasting.",
                cover_image="/static/uploads/projects/weather-cover.jpg",
                technologies="Python,FastAPI,HTMX,Chart.js",
                github_url="https://github.com/yourusername/weather",
                demo_url="https://weather.example.com",
                order=3
            ),
        ]
        
        for project in projects:
            db.add(project)
        
        db.commit()
        
        # Add project images
        for i, project in enumerate(db.query(Project).all(), 1):
            images = [
                ProjectImage(
                    project_id=project.id,
                    image_path=f"/static/uploads/projects/project{i}-img1.jpg",
                    caption="Screenshot 1",
                    order=1
                ),
                ProjectImage(
                    project_id=project.id,
                    image_path=f"/static/uploads/projects/project{i}-img2.jpg",
                    caption="Screenshot 2",
                    order=2
                ),
            ]
            for img in images:
                db.add(img)
        
        db.commit()
        
        # Add Blog Posts
        blog_posts = [
            BlogPost(
                slug="fastapi-htmx-guide",
                title="Building Modern Web Apps with FastAPI and HTMX",
                excerpt="Discover how to create dynamic, interactive web applications without heavy JavaScript frameworks.",
                content="""FastAPI and HTMX are a powerful combination for building modern web applications. In this post, I'll share my experience and best practices for using these technologies together.

## Why FastAPI?

FastAPI is incredibly fast, easy to learn, and provides automatic API documentation. It's perfect for building both APIs and server-rendered applications.

## Why HTMX?

HTMX allows you to access modern browser features directly from HTML, without writing JavaScript. This means you can build dynamic, interactive applications with much less complexity.

## Getting Started

The combination allows you to build full-stack applications with Python as your primary language, keeping your tech stack simple and maintainable.""",
                cover_image="/static/uploads/blog/fastapi-htmx-cover.jpg",
                tags="Python,FastAPI,HTMX,Web Development",
                published_at=datetime(2024, 12, 1)
            ),
            BlogPost(
                slug="python-best-practices",
                title="Python Best Practices for Production",
                excerpt="Essential patterns and practices for writing production-ready Python code.",
                content="""Writing Python code is easy, but writing production-ready Python code requires attention to detail and adherence to best practices.

## Type Hints

Always use type hints. They make your code more maintainable and catch errors early.

## Error Handling

Proper error handling is crucial. Use specific exceptions and provide meaningful error messages.

## Testing

Write tests. Use pytest and aim for good coverage of critical paths.""",
                cover_image="/static/uploads/blog/python-practices-cover.jpg",
                tags="Python,Best Practices,Software Engineering",
                published_at=datetime(2024, 11, 15)
            ),
            BlogPost(
                slug="developer-productivity",
                title="10 Tips for Developer Productivity",
                excerpt="Practical tips to boost your productivity as a developer.",
                content="""As developers, we're always looking for ways to be more productive. Here are my top 10 tips:

1. Master your editor/IDE
2. Use keyboard shortcuts
3. Automate repetitive tasks
4. Take regular breaks
5. Write clear documentation
6. Use version control effectively
7. Learn to debug efficiently
8. Stay curious and keep learning
9. Contribute to open source
10. Build side projects

Each of these has helped me become a better, more efficient developer.""",
                cover_image="/static/uploads/blog/productivity-cover.jpg",
                tags="Productivity,Tips,Career",
                published_at=datetime(2024, 11, 1)
            ),
        ]
        
        for post in blog_posts:
            db.add(post)
        
        db.commit()
        
        # Add blog images
        for i, post in enumerate(db.query(BlogPost).all(), 1):
            images = [
                BlogImage(
                    blog_post_id=post.id,
                    image_path=f"/static/uploads/blog/blog{i}-img1.jpg",
                    caption="Illustration",
                    order=1
                ),
            ]
            for img in images:
                db.add(img)
        
        db.commit()
        
        # Add Skills
        skills = [
            # Backend
            Skill(category="Backend", name="Python", level=90, order=1),
            Skill(category="Backend", name="FastAPI", level=85, order=2),
            Skill(category="Backend", name="Django", level=80, order=3),
            Skill(category="Backend", name="Node.js", level=75, order=4),
            Skill(category="Backend", name="PostgreSQL", level=85, order=5),
            
            # Frontend
            Skill(category="Frontend", name="HTML/CSS", level=90, order=1),
            Skill(category="Frontend", name="JavaScript", level=85, order=2),
            Skill(category="Frontend", name="HTMX", level=80, order=3),
            Skill(category="Frontend", name="React", level=75, order=4),
            Skill(category="Frontend", name="Tailwind CSS", level=85, order=5),
            
            # Tools & DevOps
            Skill(category="Tools & DevOps", name="Git", level=90, order=1),
            Skill(category="Tools & DevOps", name="Docker", level=80, order=2),
            Skill(category="Tools & DevOps", name="Linux", level=85, order=3),
            Skill(category="Tools & DevOps", name="CI/CD", level=75, order=4),
            Skill(category="Tools & DevOps", name="AWS", level=70, order=5),
        ]
        
        for skill in skills:
            db.add(skill)
        
        db.commit()
        
        print("✅ Database seeded successfully!")
        print(f"   - {len(projects)} projects added")
        print(f"   - {len(blog_posts)} blog posts added")
        print(f"   - {len(skills)} skills added")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
