#!/usr/bin/env python3
"""
Final comprehensive database status checker.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, inspect, text
from src.config.settings import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_comprehensive_db_status():
    """Check comprehensive database status."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        # Check connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("✅ Database connection: SUCCESS")
        
        # Get all tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Define all expected tables by category
        core_tables = ['users', 'employees', 'departments', 'shift_master']
        hr_tables = ['attendance', 'leave_management', 'payroll_setup', 'onboarding_process', 'off_boarding']
        employee_detail_tables = ['employee_personal_details', 'bank_details', 'assets', 'educational_qualifications', 'employee_documents', 'employee_work_experience']
        other_tables = ['job_titles', 'employee_expenses', 'time_entries', 'policy_master', 'events_holidays', 'compliance_documents_and_policy_management']
        system_tables = ['alembic_version']
        
        all_expected = core_tables + hr_tables + employee_detail_tables + other_tables
        
        print(f"\n📊 Database Tables Analysis:")
        print(f"  Total existing tables: {len(existing_tables)}")
        print(f"  Expected business tables: {len(all_expected)}")
        
        # Check each category
        categories = [
            ("Core Tables", core_tables),
            ("HR Management Tables", hr_tables), 
            ("Employee Detail Tables", employee_detail_tables),
            ("Other Business Tables", other_tables),
            ("System Tables", system_tables)
        ]
        
        all_good = True
        for category_name, tables in categories:
            missing = [t for t in tables if t not in existing_tables]
            existing = [t for t in tables if t in existing_tables]
            
            print(f"\n📋 {category_name}:")
            print(f"  Expected: {len(tables)}, Existing: {len(existing)}, Missing: {len(missing)}")
            
            if existing:
                print(f"  ✅ Existing: {', '.join(existing)}")
            if missing:
                print(f"  ❌ Missing: {', '.join(missing)}")
                all_good = False
        
        # Check for unexpected tables
        unexpected = [t for t in existing_tables if t not in all_expected + system_tables]
        if unexpected:
            print(f"\n🔍 Unexpected tables found: {', '.join(unexpected)}")
        
        # Final status
        if all_good:
            print(f"\n🎉 DATABASE STATUS: PERFECT!")
            print(f"   All {len(all_expected)} expected business tables exist")
            print(f"   Database is ready for HRMS operations")
        else:
            print(f"\n⚠️ DATABASE STATUS: INCOMPLETE")
            print(f"   Some tables are missing - run database initialization")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def main():
    """Main function."""
    print("🔍 HRMS Database Comprehensive Status Check\n")
    print("=" * 50)
    
    success = check_comprehensive_db_status()
    
    print("\n" + "=" * 50)
    if success:
        print("🎊 HRMS Database is fully ready!")
    else:
        print("💡 Run 'python src/scripts/init_db.py' to fix missing tables")

if __name__ == "__main__":
    main()