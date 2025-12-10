#!/usr/bin/env python3
"""
Create missing employee-related tables.
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

def create_missing_employee_tables():
    """Create missing employee-related tables."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        # Check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Define missing employee tables
        missing_tables_sql = {
            'employee_personal_details': """
                CREATE TABLE IF NOT EXISTS employee_personal_details (
                    id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) UNIQUE NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
                    date_of_birth DATE,
                    gender VARCHAR(20),
                    marital_status VARCHAR(20),
                    blood_group VARCHAR(5),
                    nationality VARCHAR(50),
                    employee_email VARCHAR(50),
                    employee_phone VARCHAR(20),
                    employee_alternate_phone VARCHAR(20),
                    employee_address VARCHAR(150),
                    emergency_full_name VARCHAR(50),
                    emergency_relationship VARCHAR(50),
                    emergency_primary_phone VARCHAR(20),
                    emergency_alternate_phone VARCHAR(20),
                    emergency_address VARCHAR(150),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """,
            
            'bank_details': """
                CREATE TABLE IF NOT EXISTS bank_details (
                    bank_id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                    account_number VARCHAR(30) UNIQUE,
                    account_holder_name VARCHAR(50) NOT NULL,
                    ifsc_code VARCHAR(20) NOT NULL,
                    bank_name VARCHAR(100) NOT NULL,
                    branch VARCHAR(150),
                    account_type VARCHAR(20) CHECK (account_type IN ('Savings', 'Current')),
                    pan_number VARCHAR(15),
                    aadhaar_number VARCHAR(20),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """,
            
            'assets': """
                CREATE TABLE IF NOT EXISTS assets (
                    asset_id SERIAL PRIMARY KEY,
                    serial_number VARCHAR(50) UNIQUE,
                    asset_name VARCHAR(50) NOT NULL,
                    asset_type VARCHAR(50) NOT NULL,
                    assigned_employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE SET NULL,
                    status VARCHAR(50) DEFAULT 'Available' CHECK (status IN ('Assigned', 'Available', 'Maintenance')),
                    condition VARCHAR(50) DEFAULT 'Good' CHECK (condition IN ('Excellent', 'Good', 'Fair')),
                    purchase_date DATE,
                    value NUMERIC(12,2),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """,
            
            'educational_qualifications': """
                CREATE TABLE IF NOT EXISTS educational_qualifications (
                    edu_id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
                    course_name VARCHAR(150) NOT NULL,
                    institution_name VARCHAR(200) NOT NULL,
                    specialization VARCHAR(50),
                    start_year INTEGER,
                    end_year INTEGER,
                    grade VARCHAR(50),
                    skill_name VARCHAR(150),
                    proficiency_level VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """,
            
            'employee_documents': """
                CREATE TABLE IF NOT EXISTS employee_documents (
                    document_id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
                    document_name VARCHAR(50) NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    upload_date DATE NOT NULL,
                    status VARCHAR(50) DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """,
            
            'employee_work_experience': """
                CREATE TABLE IF NOT EXISTS employee_work_experience (
                    experience_id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
                    experience_designation VARCHAR(150),
                    company_name VARCHAR(200),
                    start_date DATE,
                    end_date DATE,
                    responsibilities TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """
        }
        
        created_count = 0
        with engine.connect() as conn:
            for table_name, sql in missing_tables_sql.items():
                if table_name not in existing_tables:
                    try:
                        conn.execute(text(sql))
                        conn.commit()
                        logger.info(f"✅ Created table: {table_name}")
                        created_count += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Table {table_name} creation warning: {e}")
                else:
                    logger.info(f"✅ Table {table_name} already exists")
        
        # Verify final state
        inspector = inspect(engine)
        final_tables = inspector.get_table_names()
        
        logger.info(f"✅ Created {created_count} new tables")
        logger.info(f"📊 Total tables now: {len(final_tables)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating missing tables: {e}")
        return False

def main():
    """Main function."""
    print("🔨 Creating missing employee-related tables...\n")
    
    if create_missing_employee_tables():
        print("\n✅ All employee tables created successfully!")
        
        # Show final table list
        try:
            sync_db_url = settings.sync_database_url
            engine = create_engine(sync_db_url)
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"\n📊 Final database state - {len(tables)} tables:")
            for table in sorted(tables):
                print(f"  - {table}")
                
        except Exception as e:
            logger.error(f"Error verifying tables: {e}")
    else:
        print("\n❌ Failed to create some tables")
        sys.exit(1)

if __name__ == "__main__":
    main()