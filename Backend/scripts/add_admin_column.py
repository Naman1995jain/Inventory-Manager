import sys
import os

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Boolean, Column
from app.core.database import engine
from sqlalchemy.sql import text

def add_admin_column():
    """Add is_admin column to users table"""
    try:
        # Check if column exists
        with engine.connect() as connection:
            # Check if column exists
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='is_admin'"))
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                print("Adding is_admin column to users table...")
                connection.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE"))
                print("Column added successfully!")
            else:
                print("is_admin column already exists in users table.")
    except Exception as e:
        print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_admin_column()