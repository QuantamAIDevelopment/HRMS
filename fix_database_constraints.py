#!/usr/bin/env python3
"""
Fix database constraints and indexes.
This script will clean up duplicate or problematic constraints/indexes.

Usage:
    python fix_database_constraints.py
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, text, inspect
from src.config.settings import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_duplicate_indexes():
    """Fix duplicate indexes that might be causing issues."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        with engine.connect() as conn:
            # List of problematic indexes that might exist
            problematic_indexes = [
                'ix_time_entries_time_entry_id',
                'ix_employees_employee_id',
                'ix_departments_department_id',
                'ix_attendance_attendance_id'
            ]
            
            for index_name in problematic_indexes:
                try:
                    # Check if index exists
                    result = conn.execute(text(f"""
                        SELECT indexname FROM pg_indexes 
                        WHERE indexname = '{index_name}'
                    """))
                    
                    if result.fetchone():
                        logger.info(f"Found index: {index_name}")
                        
                        # Drop the index if it exists (it will be recreated properly)
                        conn.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
                        conn.commit()
                        logger.info(f"Dropped index: {index_name}")
                        
                except Exception as e:
                    logger.warning(f"Could not process index {index_name}: {e}")
            
            logger.info("Index cleanup completed")
            
    except Exception as e:
        logger.error(f"Error fixing indexes: {e}")
        raise


def check_table_constraints():
    """Check and report on table constraints."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Checking constraints for {len(tables)} tables...")
        
        for table_name in tables:
            try:
                # Get foreign keys
                fks = inspector.get_foreign_keys(table_name)
                if fks:
                    logger.info(f"Table {table_name}: {len(fks)} foreign keys")
                
                # Get indexes
                indexes = inspector.get_indexes(table_name)
                if indexes:
                    logger.info(f"Table {table_name}: {len(indexes)} indexes")
                    
            except Exception as e:
                logger.warning(f"Could not check constraints for {table_name}: {e}")
        
    except Exception as e:
        logger.error(f"Error checking constraints: {e}")


def main():
    """Main function to fix database constraints."""
    print("🔧 Fixing database constraints and indexes...\n")
    
    try:
        # First check what we have
        check_table_constraints()
        
        print("\n🧹 Cleaning up problematic indexes...")
        fix_duplicate_indexes()
        
        print("\n✅ Database constraint fixes completed!")
        print("💡 You can now restart your application.")
        
    except Exception as e:
        print(f"\n❌ Error fixing constraints: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()