#!/usr/bin/env python3
"""
Check the actual employee_work_experience table schema.
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

def check_work_experience_schema():
    """Check the actual employee_work_experience table schema."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        with engine.connect() as conn:
            # Get column information
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'employee_work_experience'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            
            print("🔍 employee_work_experience table schema:")
            print("=" * 70)
            
            if columns:
                for col in columns:
                    print(f"  {col[0]:<30} | {col[1]:<20} | Nullable: {col[2]:<3} | Default: {col[3] or 'None'}")
            else:
                print("  ❌ No columns found or table doesn't exist")
            
            print("=" * 70)
            
        return columns
        
    except Exception as e:
        logger.error(f"Error checking schema: {e}")
        return []

def main():
    """Main function."""
    print("🔍 Checking employee_work_experience table schema...\n")
    
    columns = check_work_experience_schema()
    
    if columns:
        print(f"\n✅ Found {len(columns)} columns")
        
        # Check for missing columns
        expected_columns = ['description', 'responsibilities']
        existing_column_names = [col[0] for col in columns]
        
        missing_columns = [col for col in expected_columns if col not in existing_column_names]
        
        if missing_columns:
            print(f"\n❌ Missing columns: {missing_columns}")
        else:
            print(f"\n✅ All expected columns exist!")
    else:
        print("\n❌ Schema check failed!")

if __name__ == "__main__":
    main()