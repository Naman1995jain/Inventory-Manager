import sys
import os

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.models.models import User
from app.core.security import get_password_hash
from app.core.database import SessionLocal

# Admin user details
ADMIN_EMAIL = "namanjain34710@gmail.com"
ADMIN_PASSWORD = "123456789"

def create_admin_user():
    """Create or update admin user with specified email and password"""
    db = SessionLocal()
    try:
        # Check if user already exists
        user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        
        if user:
            print(f"User with email {ADMIN_EMAIL} already exists. Updating to admin...")
            user.is_admin = True
            user.hashed_password = get_password_hash(ADMIN_PASSWORD)
        else:
            print(f"Creating new admin user with email {ADMIN_EMAIL}...")
            user = User(
                email=ADMIN_EMAIL,
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                is_admin=True
            )
            db.add(user)
        
        db.commit()
        print("Admin user created/updated successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error creating/updating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()