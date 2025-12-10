#!/usr/bin/env python3
"""
Test the finalized database initialization.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.scripts.init_db import init_database
from sqlalchemy import create_engine, inspect
from src.config.settings import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_init():
    """Test the database initialization."""
    print("🧪 Testing database initialization...\n")
    
    try:
        # Run the initialization
        await init_database()
        
        # Verify all tables exist
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'users', 'employees', 'departments', 'shift_master', 'job_titles',
            'attendance', 'leave_management', 'employee_expenses', 'payroll_setup',
            'time_entries', 'policy_master', 'events_holidays', 'off_boarding',
            'onboarding_process', 'compliance_documents_and_policy_management'
        ]
        
        missing = [table for table in required_tables if table not in tables]
        
        print(f"\n📊 Database Status:")
        print(f"  Total tables: {len(tables)}")
        print(f"  Required tables: {len(required_tables)}")
        print(f"  Missing tables: {len(missing)}")
        
        if missing:
            print(f"  ❌ Missing: {missing}")
            return False
        else:
            print(f"  ✅ All required tables exist!")
            return True
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_database_init())
    if success:
        print("\n🎉 Database initialization test PASSED!")
    else:
        print("\n💥 Database initialization test FAILED!")
        sys.exit(1)