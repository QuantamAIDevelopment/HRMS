#!/usr/bin/env python3
"""
Check the actual shift_master table schema in the database.
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

def check_shift_master_schema():
    """Check the actual shift_master table schema."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        with engine.connect() as conn:
            # Get column information for shift_master table
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'shift_master'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            
            print("🔍 shift_master table schema:")
            print("=" * 50)
            
            if columns:
                for col in columns:
                    print(f"  {col[0]:<20} | {col[1]:<15} | Nullable: {col[2]:<3} | Default: {col[3] or 'None'}")
            else:
                print("  ❌ No columns found or table doesn't exist")
            
            print("=" * 50)
            
            # Also check if there are any indexes or constraints
            result = conn.execute(text("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'shift_master'
            """))
            
            indexes = result.fetchall()
            if indexes:
                print("\n📋 Indexes:")
                for idx in indexes:
                    print(f"  - {idx[0]}: {idx[1]}")
            
        return True
        
    except Exception as e:
        logger.error(f"Error checking schema: {e}")
        return False

def main():
    """Main function."""
    print("🔍 Checking shift_master table schema...\n")
    
    if check_shift_master_schema():
        print("\n✅ Schema check completed!")
    else:
        print("\n❌ Schema check failed!")

if __name__ == "__main__":
    main()