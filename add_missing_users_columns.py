#!/usr/bin/env python3
"""
Add missing columns to users table.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, text
from src.config.settings import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_users_columns():
    """Add missing columns to users table."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        # Define the missing columns to add
        columns_to_add = [
            "employee_id VARCHAR(50) UNIQUE",
            "full_name VARCHAR(255) NOT NULL DEFAULT ''", 
            "role VARCHAR(50) NOT NULL DEFAULT 'EMPLOYEE'"
        ]
        
        with engine.connect() as conn:
            for column_def in columns_to_add:
                try:
                    # Add each column
                    sql = f"ALTER TABLE users ADD COLUMN {column_def}"
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"✅ Added column: {column_def}")
                    
                except Exception as e:
                    if "already exists" in str(e):
                        logger.info(f"⚠️ Column already exists: {column_def}")
                    else:
                        logger.error(f"❌ Error adding column {column_def}: {e}")
                        raise
        
        # Add index for employee_id if it doesn't exist
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_employee_id ON users (employee_id)"))
            conn.commit()
            logger.info("✅ Added index for employee_id")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
        
        print("\n🎉 Successfully added all missing columns to users table!")
        return True
        
    except Exception as e:
        logger.error(f"Error adding columns: {e}")
        return False

def verify_users_columns():
    """Verify that all columns now exist."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """))
            
            columns = [row[0] for row in result.fetchall()]
            
            expected_columns = ['employee_id', 'full_name', 'role']
            missing = [col for col in expected_columns if col not in columns]
            
            if missing:
                print(f"❌ Still missing columns: {missing}")
                return False
            else:
                print(f"✅ All expected columns now exist in users table!")
                print(f"📋 Total columns: {len(columns)}")
                return True
                
    except Exception as e:
        logger.error(f"Error verifying columns: {e}")
        return False

def main():
    """Main function."""
    print("🔧 Adding missing columns to users table...\n")
    
    if add_missing_users_columns():
        print("\n🔍 Verifying columns...")
        if verify_users_columns():
            print("\n🎊 Users table schema is now complete!")
        else:
            print("\n⚠️ Some columns may still be missing")
    else:
        print("\n💥 Failed to add columns")
        sys.exit(1)

if __name__ == "__main__":
    main()