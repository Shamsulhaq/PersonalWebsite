#!/usr/bin/env python3
"""
Admin Setup Script
Creates a new admin user for the personal website.
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import AdminUser
from app.init_db import init_db

def create_admin():
    # Initialize database
    init_db()
    
    db = SessionLocal()
    
    try:
        print("=== Create Admin User ===\n")
        
        username = input("Enter username: ").strip()
        if not username:
            print("❌ Username cannot be empty")
            return
        
        # Check if username exists
        existing = db.query(AdminUser).filter(AdminUser.username == username).first()
        if existing:
            print(f"❌ Username '{username}' already exists")
            return
        
        email = input("Enter email: ").strip()
        if not email:
            print("❌ Email cannot be empty")
            return
        
        # Check if email exists
        existing = db.query(AdminUser).filter(AdminUser.email == email).first()
        if existing:
            print(f"❌ Email '{email}' already exists")
            return
        
        password = input("Enter password: ").strip()
        if not password or len(password) < 6:
            print("❌ Password must be at least 6 characters")
            return
        
        confirm_password = input("Confirm password: ").strip()
        if password != confirm_password:
            print("❌ Passwords do not match")
            return
        
        # Create admin user
        admin = AdminUser(
            username=username,
            email=email,
            hashed_password=AdminUser.hash_password(password)
        )
        
        db.add(admin)
        db.commit()
        
        print(f"\n✅ Admin user '{username}' created successfully!")
        print(f"\nYou can now login at: http://localhost:8000/admin/login")
        print(f"Username: {username}")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
