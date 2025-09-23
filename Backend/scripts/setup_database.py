#!/usr/bin/env python3
"""
Database setup script for the Inventory Management System.
This script creates the database tables and sets up initial data.
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import create_tables, engine, Base
from app.models import User, Product, Warehouse, StockMovement, StockTransfer
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Check if we can connect to the database"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        logger.error("Please ensure:")
        logger.error("1. PostgreSQL is running")
        logger.error("2. Database credentials in .env are correct")
        logger.error("3. Database 'inventory_db' exists")
        return False

def create_database_tables():
    """Create all database tables"""
    try:
        create_tables()
        logger.info("✓ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to create tables: {e}")
        return False

def create_default_warehouses():
    """Create default warehouses"""
    try:
        from app.core.database import SessionLocal
        from app.models.models import Warehouse
        
        db = SessionLocal()
        
        # Check if warehouses already exist
        existing_warehouses = db.query(Warehouse).count()
        if existing_warehouses > 0:
            logger.info(f"✓ {existing_warehouses} warehouses already exist")
            db.close()
            return True
        
        # Create default warehouses
        default_warehouses = [
            {
                "name": "Main Warehouse",
                "location": "Downtown Office",
                "description": "Primary storage facility"
            },
            {
                "name": "Secondary Warehouse", 
                "location": "Industrial District",
                "description": "Backup storage facility"
            }
        ]
        
        for warehouse_data in default_warehouses:
            warehouse = Warehouse(**warehouse_data)
            db.add(warehouse)
        
        db.commit()
        db.close()
        logger.info("✓ Default warehouses created successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to create default warehouses: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting database setup...")
    
    # Check database connection
    if not check_database_connection():
        sys.exit(1)
    
    # Create tables
    if not create_database_tables():
        sys.exit(1)
    
    # Create default data
    if not create_default_warehouses():
        sys.exit(1)
    
    logger.info("✅ Database setup completed successfully!")
    logger.info("You can now start the application with: uvicorn main:app --reload")

if __name__ == "__main__":
    main()