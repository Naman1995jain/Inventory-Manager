#!/usr/bin/env python3
"""
Database migration script to simplify User table
Removes username, full_name, is_active, is_superuser, updated_at columns
Keeps only id, email, hashed_password, created_at
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def migrate_user_table():
    """Migrate the users table to simplified schema"""
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()
        
        try:
            logger.info("🔄 Starting user table migration...")
            
            # 1. Create a backup of the current users table
            logger.info("📋 Creating backup of users table...")
            connection.execute(text("""
                CREATE TABLE users_backup AS 
                SELECT * FROM users;
            """))
            
            # 2. Create new simplified users table
            logger.info("🔨 Creating new simplified users table...")
            connection.execute(text("""
                CREATE TABLE users_new (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
                );
            """))
            
            # 3. Copy data from old table to new table
            logger.info("📊 Migrating data to new table...")
            connection.execute(text("""
                INSERT INTO users_new (id, email, hashed_password, created_at)
                SELECT id, email, hashed_password, created_at 
                FROM users;
            """))
            
            # 4. Drop the old users table
            logger.info("🗑️ Dropping old users table...")
            connection.execute(text("DROP TABLE users CASCADE;"))
            
            # 5. Rename the new table to users
            logger.info("🔄 Renaming new table to users...")
            connection.execute(text("ALTER TABLE users_new RENAME TO users;"))
            
            # 6. Create indexes
            logger.info("📈 Creating indexes...")
            connection.execute(text("CREATE INDEX ix_users_id ON users (id);"))
            connection.execute(text("CREATE UNIQUE INDEX ix_users_email ON users (email);"))
            
            # 7. Update sequence
            logger.info("🔢 Updating sequence...")
            connection.execute(text("""
                SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
            """))
            
            # 8. Recreate foreign key constraints for related tables
            logger.info("🔗 Recreating foreign key constraints...")
            
            # Products table
            connection.execute(text("""
                ALTER TABLE products 
                ADD CONSTRAINT products_created_by_fkey 
                FOREIGN KEY (created_by) REFERENCES users (id);
            """))
            
            # Stock movements table
            connection.execute(text("""
                ALTER TABLE stock_movements 
                ADD CONSTRAINT stock_movements_created_by_fkey 
                FOREIGN KEY (created_by) REFERENCES users (id);
            """))
            
            # Stock transfers table
            connection.execute(text("""
                ALTER TABLE stock_transfers 
                ADD CONSTRAINT stock_transfers_created_by_fkey 
                FOREIGN KEY (created_by) REFERENCES users (id);
            """))
            
            # Commit transaction
            trans.commit()
            logger.info("✅ User table migration completed successfully!")
            
            # Show final table structure
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position;
            """))
            
            logger.info("📋 New users table structure:")
            for row in result:
                logger.info(f"  - {row.column_name}: {row.data_type} ({'NULL' if row.is_nullable == 'YES' else 'NOT NULL'})")
                
        except Exception as e:
            # Rollback on error
            trans.rollback()
            logger.error(f"❌ Migration failed: {e}")
            logger.info("🔄 Rolling back changes...")
            raise
            
        finally:
            logger.info("🏁 Migration process completed")

if __name__ == "__main__":
    try:
        migrate_user_table()
        print("\n🎉 Migration completed successfully!")
        print("You can now start the application with the simplified authentication.")
    except Exception as e:
        print(f"\n💥 Migration failed: {e}")
        print("Please check the logs and fix any issues before retrying.")
        sys.exit(1)