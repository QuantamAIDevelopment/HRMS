#!/usr/bin/env python3
"""
Finalized database initialization script.
This script checks if tables exist and creates them only if needed.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from config.settings import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    try:
        # Extract database name from URL
        db_url = settings.database_url
        db_name = db_url.split('/')[-1]
        
        # Create connection to postgres database (not the target database)
        postgres_url = db_url.rsplit('/', 1)[0] + '/postgres'
        
        # Use sync engine for database creation
        sync_postgres_url = postgres_url.replace("postgresql+asyncpg://", "postgresql://")
        engine = create_engine(sync_postgres_url)
        
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            if not result.fetchone():
                # Create database
                conn.execute(text("COMMIT"))  # End any transaction
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"✅ Created database: {db_name}")
            else:
                logger.info(f"✅ Database {db_name} already exists")
                
    except Exception as e:
        logger.error(f"❌ Error creating database: {e}")
        raise


async def check_and_create_tables():
    """Check if tables exist and create them if needed."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        # Check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Define required tables
        required_tables = [
            'users', 'employees', 'departments', 'shift_master', 'job_titles',
            'attendance', 'leave_management', 'employee_expenses', 'payroll_setup',
            'time_entries', 'policy_master', 'events_holidays', 'off_boarding',
            'onboarding_process', 'compliance_documents_and_policy_management',
            'employee_personal_details', 'bank_details', 'assets', 
            'educational_qualifications', 'employee_documents', 'employee_work_experience'
        ]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if not missing_tables:
            logger.info(f"✅ All {len(required_tables)} tables already exist")
            return True
        
        logger.info(f"📋 Found {len(existing_tables)} existing tables")
        logger.info(f"🔨 Need to create {len(missing_tables)} missing tables: {missing_tables}")
        
        # Create missing tables using SQL
        await create_missing_tables_sql(engine, missing_tables)
        
        # Verify all tables are created
        inspector = inspect(engine)
        final_tables = inspector.get_table_names()
        final_missing = [table for table in required_tables if table not in final_tables]
        
        if final_missing:
            logger.error(f"❌ Still missing tables: {final_missing}")
            return False
        
        logger.info(f"✅ All {len(final_tables)} tables are now available")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking/creating tables: {e}")
        raise


async def create_missing_tables_sql(engine, missing_tables):
    """Create missing tables using raw SQL."""
    
    table_sql = {
        'users': """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                is_superuser BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'departments': """
            CREATE TABLE IF NOT EXISTS departments (
                department_id SERIAL PRIMARY KEY,
                department_name VARCHAR(100) UNIQUE NOT NULL
            )
        """,
        
        'shift_master': """
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
        """,
        
        'employees': """
            CREATE TABLE IF NOT EXISTS employees (
                employee_id VARCHAR(50) PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                department_id INTEGER REFERENCES departments(department_id),
                designation VARCHAR(50) NOT NULL,
                joining_date DATE NOT NULL,
                reporting_manager VARCHAR(50),
                email_id VARCHAR(100) UNIQUE NOT NULL,
                phone_number VARCHAR(20) NOT NULL,
                location VARCHAR(50),
                shift_id INTEGER REFERENCES shift_master(shift_id),
                employee_type VARCHAR(50) NOT NULL,
                annual_ctc VARCHAR(50) DEFAULT '0',
                annual_leaves INTEGER DEFAULT 21,
                profile_photo VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'job_titles': """
            CREATE TABLE IF NOT EXISTS job_titles (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                department VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'policy_master': """
            CREATE TABLE IF NOT EXISTS policy_master (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                policy_type VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'attendance': """
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id SERIAL PRIMARY KEY,
                employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                attendance_date DATE NOT NULL,
                punch_in TIME,
                punch_out TIME,
                work_hours NUMERIC(5,2),
                status VARCHAR(50),
                policy_id UUID REFERENCES policy_master(id),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'leave_management': """
            CREATE TABLE IF NOT EXISTS leave_management (
                leave_id SERIAL PRIMARY KEY,
                employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                leave_type VARCHAR(100) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                reason TEXT,
                status VARCHAR(50) DEFAULT 'Pending',
                employee_used_leaves INTEGER,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'employee_expenses': """
            CREATE TABLE IF NOT EXISTS employee_expenses (
                expense_id SERIAL PRIMARY KEY,
                employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                category VARCHAR(100) NOT NULL,
                description TEXT,
                amount NUMERIC(12,2) NOT NULL,
                expense_date DATE NOT NULL,
                status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'payroll_setup': """
            CREATE TABLE IF NOT EXISTS payroll_setup (
                payroll_id SERIAL PRIMARY KEY,
                employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                designation VARCHAR(100) NOT NULL,
                pay_cycle VARCHAR(20) DEFAULT 'Monthly',
                basic_salary NUMERIC(12,2) DEFAULT 0,
                hra NUMERIC(12,2) DEFAULT 0,
                allowance NUMERIC(12,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'time_entries': """
            CREATE TABLE IF NOT EXISTS time_entries (
                time_entry_id SERIAL PRIMARY KEY,
                employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                entry_date DATE NOT NULL,
                project VARCHAR(150) NOT NULL,
                task_description TEXT NOT NULL,
                hours NUMERIC(5,2) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'events_holidays': """
            CREATE TABLE IF NOT EXISTS events_holidays (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                type VARCHAR(100),
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'off_boarding': """
            CREATE TABLE IF NOT EXISTS off_boarding (
                id SERIAL PRIMARY KEY,
                employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                reason VARCHAR(255),
                last_working_day DATE,
                status VARCHAR(50) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'onboarding_process': """
            CREATE TABLE IF NOT EXISTS onboarding_process (
                onboarding_id SERIAL PRIMARY KEY,
                employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                name VARCHAR(50) NOT NULL,
                position VARCHAR(50) NOT NULL,
                department VARCHAR(50) NOT NULL,
                joining_date DATE NOT NULL,
                shifts VARCHAR(100),
                status VARCHAR(50) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
        'compliance_documents_and_policy_management': """
            CREATE TABLE IF NOT EXISTS compliance_documents_and_policy_management (
                document_id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description TEXT,
                uploaded_document TEXT,
                uploaded_by VARCHAR(50) REFERENCES employees(employee_id),
                uploaded_on TIMESTAMP DEFAULT NOW(),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """,
        
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
    
    # Create tables in dependency order
    creation_order = [
        'users', 'departments', 'shift_master', 'employees', 'job_titles', 
        'policy_master', 'employee_personal_details', 'bank_details', 'assets',
        'educational_qualifications', 'employee_documents', 'employee_work_experience',
        'attendance', 'leave_management', 'employee_expenses', 'payroll_setup', 
        'time_entries', 'events_holidays', 'off_boarding', 'onboarding_process', 
        'compliance_documents_and_policy_management'
    ]
    
    with engine.connect() as conn:
        for table_name in creation_order:
            if table_name in missing_tables:
                try:
                    conn.execute(text(table_sql[table_name]))
                    conn.commit()
                    logger.info(f"✅ Created table: {table_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Table {table_name} creation warning: {e}")


async def init_database():
    """Initialize the database by creating database and tables if needed."""
    logger.info("🚀 Starting database initialization...")
    
    try:
        # Step 1: Create database if it doesn't exist
        await create_database_if_not_exists()
        
        # Step 2: Check and create tables if needed
        success = await check_and_create_tables()
        
        if success:
            logger.info("🎉 Database initialization completed successfully!")
        else:
            logger.error("❌ Database initialization failed!")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_database())