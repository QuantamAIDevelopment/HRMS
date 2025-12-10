#!/usr/bin/env python3
"""
Test that the work experience model fix works.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import settings
from src.models.Employee_models import EmployeeWorkExperience
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_work_experience_query():
    """Test querying work experience to see if the schema mismatch is fixed."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        
        # Try to query work experience (this was failing before)
        work_experiences = db.query(EmployeeWorkExperience).limit(1).all()
        
        print("✅ Work experience query successful!")
        print(f"📊 Found {len(work_experiences)} work experience records")
        
        if work_experiences:
            exp = work_experiences[0]
            print(f"📋 Sample record: {exp.company_name} - {exp.experience_designation}")
            print(f"📝 Responsibilities: {exp.responsibilities}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Work experience query failed: {e}")
        return False

def main():
    """Main function."""
    print("🧪 Testing work experience model fix...\n")
    
    if test_work_experience_query():
        print("\n🎉 Work experience model is now working correctly!")
        print("✅ The Complete Employee API should work for work experience data")
    else:
        print("\n💥 Work experience model still has issues")

if __name__ == "__main__":
    main()