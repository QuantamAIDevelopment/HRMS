#!/usr/bin/env python3
"""
Verify all database table schemas match the SQLAlchemy models.
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

def verify_table_schema(table_name, expected_columns):
    """Verify a specific table has all expected columns."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT column_name
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            missing_columns = [col for col in expected_columns if col not in existing_columns]
            
            return existing_columns, missing_columns
            
    except Exception as e:
        logger.error(f"Error checking {table_name}: {e}")
        return [], expected_columns

def main():
    """Main function to verify all critical table schemas."""
    print("🔍 Verifying all database table schemas...\n")
    
    # Define expected columns for critical tables
    table_schemas = {
        'users': ['id', 'employee_id', 'email', 'hashed_password', 'full_name', 'role', 'is_active', 'created_at', 'updated_at'],
        'employees': ['employee_id', 'first_name', 'last_name', 'department_id', 'designation', 'joining_date', 'email_id', 'phone_number', 'shift_id', 'employee_type', 'annual_ctc'],
        'employee_personal_details': ['id', 'employee_id', 'date_of_birth', 'gender', 'marital_status', 'blood_group', 'nationality', 'employee_email', 'employee_phone', 'employee_address', 'city', 'pincode', 'country', 'state'],
        'departments': ['department_id', 'department_name'],
        'shift_master': ['shift_id', 'shift_name', 'shift_type', 'start_time', 'end_time', 'working_days'],
        'bank_details': ['bank_id', 'employee_id', 'account_number', 'account_holder_name', 'ifsc_code', 'bank_name', 'branch', 'account_type', 'pan_number', 'aadhaar_number']
    }
    
    all_good = True
    
    for table_name, expected_cols in table_schemas.items():
        existing_cols, missing_cols = verify_table_schema(table_name, expected_cols)
        
        if missing_cols:
            print(f"❌ {table_name}: Missing columns {missing_cols}")
            all_good = False
        else:
            print(f"✅ {table_name}: All {len(existing_cols)} columns present")
    
    print("\n" + "="*60)
    
    if all_good:
        print("🎉 ALL DATABASE SCHEMAS ARE COMPLETE!")
        print("✅ Your Complete Employee API should now work perfectly!")
    else:
        print("⚠️ Some tables still have missing columns")
        print("💡 Run the appropriate fix scripts for missing columns")
    
    print("="*60)

if __name__ == "__main__":
    main()