#!/usr/bin/env python3
"""
Database creation script for the Inventory Management System.
This script creates the required databases.
"""

import sys
import os
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_databases():
    """Create the required databases"""
    # Connection parameters from .env
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD")
    
    # Databases to create
    databases = ["inventory_db", "inventory_test_db"]
    
    try:
        # Connect to the default 'postgres' database
        logger.info(" Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database="postgres"  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        logger.info(" Connected to PostgreSQL server successfully")
        
        # Create each database
        for db_name in databases:
            try:
                # Check if database exists
                cursor.execute(
                    "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", 
                    (db_name,)
                )
                exists = cursor.fetchone()
                
                if exists:
                    logger.info(f"✓ Database '{db_name}' already exists")
                else:
                    # Create database
                    cursor.execute(f'CREATE DATABASE "{db_name}"')
                    logger.info(f" Created database '{db_name}' successfully")
                    
            except Exception as e:
                logger.error(f" Failed to create database '{db_name}': {e}")
                return False
        
        cursor.close()
        conn.close()
        
        logger.info(" All databases created successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        logger.error(f" Failed to connect to PostgreSQL: {e}")
        logger.error("Please ensure:")
        logger.error("1. PostgreSQL server is running")
        logger.error("2. Database credentials in .env are correct")
        logger.error("3. You can connect to PostgreSQL with the provided credentials")
        return False
    except Exception as e:
        logger.error(f" Unexpected error: {e}")
        return False

def main():
    """Main function"""
    logger.info("🗄️  Creating databases for Inventory Management System...")
    
    if create_databases():
        logger.info(" Database creation completed successfully!")
        logger.info("You can now run: python scripts/setup_database.py")
    else:
        logger.error(" Database creation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()