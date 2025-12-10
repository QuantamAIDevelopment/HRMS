#!/usr/bin/env python3
"""
Create the employees table first, then other tables.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, inspect, MetaData, Table, Column, String, Integer, Date, TIMESTAMP, text
from sqlalchemy.sql import func
from src.config.settings import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_employees_table_manually():
    """Create the employees table manually first."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        # Create employees table manually
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id VARCHAR(50) PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    department_id INTEGER NOT NULL,
                    designation VARCHAR(50) NOT NULL,
                    joining_date DATE NOT NULL,
                    reporting_manager VARCHAR(50),
                    email_id VARCHAR(100) UNIQUE NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    location VARCHAR(50),
                    shift_id INTEGER NOT NULL,
                    employee_type VARCHAR(50) NOT NULL,
                    annual_ctc VARCHAR(50) DEFAULT '0',
                    annual_leaves INTEGER DEFAULT 21,
                    profile_photo VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """))
            conn.commit()
            logger.info("✅ Employees table created manually")
            
        # Create departments table
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS departments (
                    department_id SERIAL PRIMARY KEY,
                    department_name VARCHAR(100) UNIQUE NOT NULL
                )
            """))
            conn.commit()
            logger.info("✅ Departments table created manually")
            
        # Create shift_master table
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS shift_master (
                    shift_id SERIAL PRIMARY KEY,
                    shift_name VARCHAR(150) NOT NULL,
                    shift_type VARCHAR(100) NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    working_days VARCHAR(200) DEFAULT 'Monday-Friday',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """))
            conn.commit()
            logger.info("✅ Shift_master table created manually")
            
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables manually: {e}")
        return False

def create_remaining_tables():
    """Create remaining tables using SQLAlchemy."""
    try:
        # Import base and models
        from src.models.base import Base
        
        # Import all models
        from src.models import user, job_title, timesheet, shift, off_boarding
        from src.models import events_holidays, policy, leave, hrms_models, Employee_models
        
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        # Create all remaining tables
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("✅ Remaining tables created with SQLAlchemy")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating remaining tables: {e}")
        return False

def main():
    """Main function."""
    print("🔨 Creating database tables step by step...\n")
    
    # Step 1: Create core tables manually
    logger.info("Step 1: Creating core tables manually...")
    if not create_employees_table_manually():
        print("❌ Failed to create core tables")
        sys.exit(1)
    
    # Step 2: Create remaining tables with SQLAlchemy
    logger.info("Step 2: Creating remaining tables with SQLAlchemy...")
    if not create_remaining_tables():
        print("❌ Failed to create remaining tables")
        sys.exit(1)
    
    # Step 3: Verify all tables
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        inspector = inspect(engine)
        final_tables = inspector.get_table_names()
        
        print(f"\n✅ Success! Created {len(final_tables)} tables:")
        for table in sorted(final_tables):
            print(f"  - {table}")
            
    except Exception as e:
        logger.error(f"Error verifying tables: {e}")

if __name__ == "__main__":
    main()