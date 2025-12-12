"""
Database initialization and migrations
"""
import sqlite3
from app.database import Base, engine


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    
    # Auto-migration: Add new columns if they don't exist
    conn = sqlite3.connect('personal_site.db')
    cursor = conn.cursor()
    
    try:
        # Check and add blog_posts columns
        cursor.execute("PRAGMA table_info(blog_posts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'view_count' not in columns:
            cursor.execute("ALTER TABLE blog_posts ADD COLUMN view_count INTEGER DEFAULT 0")
            print("✓ Added view_count column to blog_posts")
        
        if 'is_published' not in columns:
            cursor.execute("ALTER TABLE blog_posts ADD COLUMN is_published INTEGER DEFAULT 1")
            print("✓ Added is_published column to blog_posts")
        
        # Check and add projects columns
        cursor.execute("PRAGMA table_info(projects)")
        project_columns = [col[1] for col in cursor.fetchall()]
        
        if 'short_description' not in project_columns:
            cursor.execute("ALTER TABLE projects ADD COLUMN short_description TEXT")
            print("✓ Added short_description column to projects")
        
        conn.commit()
    except Exception as e:
        print(f"Migration note: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
