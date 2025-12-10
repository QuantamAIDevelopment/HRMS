#!/usr/bin/env python3
"""
Database connection and status checker.
Run this script to verify database connectivity and table status.

Usage:
    python check_database.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, text, inspect
from src.config.settings import settings
from src.models import Base
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_database_connection():
    """Check if we can connect to the database."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
        print("✅ Database connection: SUCCESS")
        return True
        
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return False


def check_tables():
    """Check which tables exist in the database."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Get expected tables from models
        expected_tables = list(Base.metadata.tables.keys())
        
        print(f"\n📊 Database Tables Status:")
        print(f"Expected tables: {len(expected_tables)}")
        print(f"Existing tables: {len(existing_tables)}")
        
        if existing_tables:
            print(f"\n✅ Existing tables:")
            for table in sorted(existing_tables):
                print(f"  - {table}")
        
        missing_tables = set(expected_tables) - set(existing_tables)
        if missing_tables:
            print(f"\n❌ Missing tables:")
            for table in sorted(missing_tables):
                print(f"  - {table}")
        else:
            print(f"\n🎉 All expected tables exist!")
            
        return len(missing_tables) == 0
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False


def main():
    """Main function to check database status."""
    print("🔍 Checking HRMS database status...\n")
    
    # Check connection
    connection_ok = check_database_connection()
    
    if connection_ok:
        # Check tables
        tables_ok = check_tables()
        
        if tables_ok:
            print(f"\n🎉 Database is fully set up and ready!")
        else:
            print(f"\n⚠️  Database connected but some tables are missing.")
            print(f"💡 Run 'python setup_database.py' to create missing tables.")
    else:
        print(f"\n💥 Cannot connect to database.")
        print(f"💡 Check your database configuration in .env file.")


if __name__ == "__main__":
    main()