#!/usr/bin/env python3
"""
Fix the most critical schema issues that affect the Complete Employee API.
This script focuses on the high-priority mismatches that would cause API failures.
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

def fix_critical_issues():
    """Fix the most critical schema issues that affect API functionality."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        # Critical fixes for Complete Employee API
        critical_fixes = [
            # Employee Documents - Add missing file_name column to model (it exists in DB)
            # This is handled by updating the model, not the database
            
            # Employee Expenses - Add missing columns
            "ALTER TABLE employee_expenses ADD COLUMN IF NOT EXISTS expense_code VARCHAR(20)",
            "ALTER TABLE employee_expenses ADD COLUMN IF NOT EXISTS receipt_url TEXT",
            
            # Time Entries - Add missing columns for approval workflow
            "ALTER TABLE time_entries ADD COLUMN IF NOT EXISTS approver_id VARCHAR(50)",
            "ALTER TABLE time_entries ADD COLUMN IF NOT EXISTS approver_type VARCHAR(20) DEFAULT 'MANAGER'",
            "ALTER TABLE time_entries ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'PENDING'",
            
            # Off Boarding - Add missing columns for complete off-boarding process
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS access_card_return BOOLEAN DEFAULT FALSE",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS checklist_name VARCHAR(150)",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS department VARCHAR(100)",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS description TEXT",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS email VARCHAR(150)",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS exit_interview BOOLEAN DEFAULT FALSE",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS final_settlement BOOLEAN DEFAULT FALSE",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS final_settlement_amount DECIMAL(12,2)",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS full_name VARCHAR(150)",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS it_asset_return BOOLEAN DEFAULT FALSE",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS knowledge_transfer BOOLEAN DEFAULT FALSE",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS position VARCHAR(100)",
            "ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS resignation_date DATE",
        ]
        
        print("🔧 Fixing critical schema issues...")
        
        with engine.connect() as conn:
            for i, sql in enumerate(critical_fixes, 1):
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"✅ Fixed issue {i}/{len(critical_fixes)}")
                except Exception as e:
                    if "already exists" in str(e):
                        logger.info(f"⚠️ Column already exists for fix {i}")
                    else:
                        logger.error(f"❌ Error in fix {i}: {e}")
        
        print(f"\n✅ Applied {len(critical_fixes)} critical fixes!")
        return True
        
    except Exception as e:
        logger.error(f"Error applying fixes: {e}")
        return False

def update_model_files():
    """Instructions for updating model files to match database schema."""
    
    print(f"\n🔧 REQUIRED MODEL UPDATES:")
    print("=" * 60)
    
    model_updates = [
        {
            "file": "src/models/Employee_models.py - EmployeeDocuments class",
            "action": "ADD",
            "column": "file_name = Column(String(255), nullable=False)",
            "reason": "Database has this column but model doesn't"
        },
        {
            "file": "src/models/user.py - User class", 
            "action": "ADD",
            "column": "is_superuser = Column(Boolean, default=False)",
            "reason": "Database has this column but model doesn't"
        },
        {
            "file": "src/models/events_holidays.py - EventsHolidays class",
            "action": "REPLACE columns with",
            "column": "name, date, description (match database schema)",
            "reason": "Model has different column names than database"
        },
        {
            "file": "src/models/job_title.py - JobTitle class",
            "action": "REPLACE columns with", 
            "column": "id, title, description, department (match database schema)",
            "reason": "Model has completely different schema than database"
        }
    ]
    
    for i, update in enumerate(model_updates, 1):
        print(f"\n{i}. {update['file']}")
        print(f"   Action: {update['action']}")
        print(f"   Column: {update['column']}")
        print(f"   Reason: {update['reason']}")

def main():
    """Main function."""
    print("🚀 Fixing critical schema issues for Complete Employee API...\n")
    
    if fix_critical_issues():
        update_model_files()
        
        print(f"\n" + "=" * 60)
        print("✅ CRITICAL FIXES COMPLETED!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. Update the model files as shown above")
        print("2. Restart your FastAPI server")
        print("3. Test the Complete Employee API")
        print("4. Run comprehensive_schema_audit.py again to verify fixes")
        
    else:
        print("\n❌ Failed to apply critical fixes")

if __name__ == "__main__":
    main()