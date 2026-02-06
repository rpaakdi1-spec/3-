#!/usr/bin/env python3
"""
Create admin user in database
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_admin_user():
    # Database connection - use actual credentials from container env
    DATABASE_URL = "postgresql://uvis_user:uvis_secure_password_2024@db:5432/uvis_db"
    
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        # Check if admin exists
        result = session.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": "admin"}
        )
        existing = result.fetchone()
        
        if existing:
            print("❌ Admin user already exists!")
            return
        
        # Create admin user
        hashed_password = get_password_hash("admin123")
        
        session.execute(
            text("""
                INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_superuser, created_at, updated_at)
                VALUES (:username, :email, :hashed_password, :full_name, :role, :is_active, :is_superuser, NOW(), NOW())
            """),
            {
                "username": "admin",
                "email": "admin@uvis.com",
                "hashed_password": hashed_password,
                "full_name": "System Administrator",
                "role": "ADMIN",
                "is_active": True,
                "is_superuser": True
            }
        )
        session.commit()
        
        print("✅ Admin user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@uvis.com")

if __name__ == "__main__":
    try:
        create_admin_user()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
