#!/usr/bin/env python3
"""
Verify that the critical schema fixes have been applied successfully.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import settings
from src.models.Employee_models import EmployeeDocuments, Assets
from src.models.user import User
from src.models.events_holidays import EventsHolidays
from src.models.job_title import JobTitle
from src.models.expense import Expense
from src.models.timesheet import Timesheet
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_critical_models():
    """Test that the critical models can now query the database successfully."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        
        tests = [
            ("EmployeeDocuments", lambda: db.query(EmployeeDocuments).limit(1).all()),
            ("Assets", lambda: db.query(Assets).limit(1).all()),
            ("User", lambda: db.query(User).limit(1).all()),
            ("EventsHolidays", lambda: db.query(EventsHolidays).limit(1).all()),
            ("JobTitle", lambda: db.query(JobTitle).limit(1).all()),
            ("Expense", lambda: db.query(Expense).limit(1).all()),
            ("Timesheet", lambda: db.query(Timesheet).limit(1).all()),
        ]
        
        print("🧪 Testing critical model queries...")
        print("-" * 50)
        
        all_passed = True
        
        for model_name, test_func in tests:
            try:
                result = test_func()
                print(f"✅ {model_name}: Query successful ({len(result)} records)")
            except Exception as e:
                print(f"❌ {model_name}: Query failed - {e}")
                all_passed = False
        
        db.close()
        
        print("-" * 50)
        if all_passed:
            print("🎉 All critical models are working correctly!")
        else:
            print("⚠️ Some models still have issues")
        
        return all_passed
        
    except Exception as e:
        logger.error(f"Error in model testing: {e}")
        return False

def main():
    """Main function."""
    print("🔍 Verifying critical schema fixes...\n")
    
    if test_critical_models():
        print(f"\n✅ VERIFICATION SUCCESSFUL!")
        print("🚀 Your Complete Employee API should now work without schema errors!")
        print("\n📋 Ready to test:")
        print("- Complete Employee creation")
        print("- Employee document uploads")
        print("- Asset assignments")
        print("- Time entry submissions")
        print("- All other HRMS functionality")
    else:
        print(f"\n❌ Some issues remain")
        print("💡 Run comprehensive_schema_audit.py for detailed analysis")

if __name__ == "__main__":
    main()