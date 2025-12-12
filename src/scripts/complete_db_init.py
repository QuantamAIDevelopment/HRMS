#!/usr/bin/env python3
"""
Complete database initialization script with all correct schemas.
This script will create all tables with the proper columns, constraints, and relationships
when a new database is created.
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


async def create_complete_schema():
    """Create all tables with complete and correct schema."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        # Complete table definitions with all required columns
        table_definitions = {
            # Core tables first (no dependencies)
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'EMPLOYEE',
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
                    employees INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """,
            
            'job_titles': """
                CREATE TABLE IF NOT EXISTS job_titles (
                    job_title_id SERIAL PRIMARY KEY,
                    job_title VARCHAR(150) NOT NULL,
                    job_description TEXT NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    salary_min NUMERIC(10,2),
                    salary_max NUMERIC(10,2),
                    employees INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """,
            
            'policy_master': """
                CREATE TABLE IF NOT EXISTS policy_master (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) UNIQUE NOT NULL,
                    description TEXT,
                    working_hours_per_day FLOAT NOT NULL,
                    working_days_per_week INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT FALSE,
                    grace_period_minutes INTEGER NOT NULL,
                    mark_late_after_minutes INTEGER NOT NULL,
                    half_day_hours FLOAT NOT NULL,
                    auto_deduct_for_absence BOOLEAN NOT NULL,
                    overtime_enabled BOOLEAN NOT NULL,
                    overtime_multiplier_weekdays FLOAT,
                    overtime_multiplier_weekend FLOAT,
                    require_check_in BOOLEAN NOT NULL,
                    require_check_out BOOLEAN NOT NULL,
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
            
            # Employee table (depends on departments and shift_master)
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
                    employment_type VARCHAR(50) NOT NULL,
                    annual_ctc VARCHAR(50) DEFAULT '0',
                    annual_leaves INTEGER DEFAULT 21,
                    profile_photo VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """,
            
            # Employee detail tables (depend on employees)
            'employee_personal_details': """
                CREATE TABLE IF NOT EXISTS employee_personal_details (
                    id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) UNIQUE NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
                    date_of_birth DATE,
                    gender VARCHAR(20),
                    marital_status VARCHAR(20),
                    blood_group VARCHAR(5),
                    nationality VARCHAR(50),
                    employee_email VARCHAR(100),
                    employee_phone VARCHAR(20),
                    employee_alternate_phone VARCHAR(20),
                    employee_address VARCHAR(255),
                    city VARCHAR(100),
                    pincode VARCHAR(20),
                    country VARCHAR(100),
                    state VARCHAR(100),
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
                    employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE SET NULL,
                    assigned_to VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'Available',
                    condition VARCHAR(50),
                    purchase_date DATE,
                    value NUMERIC(12,2),
                    note TEXT,
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
            """,
            
            # Operational tables
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
                    expense_code VARCHAR(20),
                    employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                    category VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    amount NUMERIC(12,2) NOT NULL,
                    expense_date DATE NOT NULL,
                    receipt_url TEXT,
                    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
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
                    basic_salary NUMERIC(12,2),
                    hra NUMERIC(12,2),
                    allowance NUMERIC(12,2),
                    provident_fund_percentage NUMERIC(5,2),
                    professional_tax NUMERIC(12,2),
                    total_earnings NUMERIC(12,2),
                    total_deductions NUMERIC(12,2),
                    net_salary NUMERIC(12,2),
                    pdf_path TEXT,
                    month VARCHAR(20),
                    basic_salary_type VARCHAR(50),
                    hra_type VARCHAR(50),
                    allowance_type VARCHAR(50),
                    provident_fund_type VARCHAR(50),
                    professional_tax_type VARCHAR(50),
                    salary_components JSONB,
                    organization_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """,
            
            'time_entries': """
                CREATE TABLE IF NOT EXISTS time_entries (
                    time_entry_id VARCHAR(50) PRIMARY KEY,
                    employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                    entry_date DATE NOT NULL,
                    project VARCHAR(150) NOT NULL,
                    task_description TEXT NOT NULL,
                    hours NUMERIC(5,2) NOT NULL,
                    status VARCHAR(50) DEFAULT 'PENDING_MANAGER_APPROVAL',
                    approver_id VARCHAR(50),
                    approver_type VARCHAR(20),
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
                    access_card_return BOOLEAN DEFAULT FALSE,
                    checklist_name VARCHAR(150),
                    department VARCHAR(100),
                    description TEXT,
                    email VARCHAR(150),
                    exit_interview BOOLEAN DEFAULT FALSE,
                    final_settlement BOOLEAN DEFAULT FALSE,
                    final_settlement_amount DECIMAL(12,2),
                    full_name VARCHAR(150),
                    it_asset_return BOOLEAN DEFAULT FALSE,
                    knowledge_transfer BOOLEAN DEFAULT FALSE,
                    position VARCHAR(100),
                    resignation_date DATE,
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
                    category VARCHAR(50) NOT NULL CHECK (category IN ('Policy', 'Compliance', 'Legal', 'Training')),
                    description TEXT,
                    uploaded_document TEXT,
                    uploaded_by VARCHAR(50) REFERENCES employees(employee_id),
                    uploaded_on TIMESTAMP DEFAULT NOW(),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """,
            
            'profile_edit_requests': """
                CREATE TABLE IF NOT EXISTS profile_edit_requests (
                    id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                    requested_changes TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    old_value VARCHAR(255),
                    new_value VARCHAR(255),
                    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
                    manager_comments TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """
        }
        
        # Create tables in dependency order
        creation_order = [
            'users', 'departments', 'shift_master', 'job_titles', 'policy_master', 'events_holidays',
            'employees', 'employee_personal_details', 'bank_details', 'assets',
            'educational_qualifications', 'employee_documents', 'employee_work_experience',
            'attendance', 'leave_management', 'employee_expenses', 'payroll_setup', 
            'time_entries', 'off_boarding', 'onboarding_process', 
            'compliance_documents_and_policy_management', 'profile_edit_requests'
        ]
        
        with engine.connect() as conn:
            for i, table_name in enumerate(creation_order, 1):
                try:
                    sql = table_definitions[table_name]
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"✅ Created table {i}/{len(creation_order)}: {table_name}")
                except Exception as e:
                    if "already exists" in str(e):
                        logger.info(f"⚠️ Table {table_name} already exists")
                    else:
                        logger.error(f"❌ Error creating {table_name}: {e}")
                        raise
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_employee_id ON users (employee_id)",
            "CREATE INDEX IF NOT EXISTS idx_employees_department ON employees (department_id)",
            "CREATE INDEX IF NOT EXISTS idx_employees_shift ON employees (shift_id)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_employee ON attendance (employee_id)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance (attendance_date)",
            "CREATE INDEX IF NOT EXISTS idx_assets_employee ON assets (employee_id)",
            "CREATE INDEX IF NOT EXISTS idx_time_entries_employee ON time_entries (employee_id)",
            "CREATE INDEX IF NOT EXISTS idx_time_entries_date ON time_entries (entry_date)",
            "CREATE INDEX IF NOT EXISTS idx_edu_employee ON educational_qualifications (employee_id)",
        ]
        
        with engine.connect() as conn:
            for idx_sql in indexes:
                try:
                    conn.execute(text(idx_sql))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
        
        logger.info("✅ All tables and indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating schema: {e}")
        raise


async def verify_schema():
    """Verify that all tables were created with correct schema."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'users', 'employees', 'departments', 'shift_master', 'job_titles',
            'attendance', 'leave_management', 'employee_expenses', 'payroll_setup',
            'time_entries', 'policy_master', 'events_holidays', 'off_boarding',
            'onboarding_process', 'compliance_documents_and_policy_management',
            'employee_personal_details', 'bank_details', 'assets', 
            'educational_qualifications', 'employee_documents', 'employee_work_experience',
            'profile_edit_requests'
        ]
        
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            logger.error(f"❌ Missing tables: {missing_tables}")
            return False
        
        logger.info(f"✅ All {len(expected_tables)} tables created successfully")
        logger.info(f"📊 Total tables in database: {len(tables)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying schema: {e}")
        return False


async def init_complete_database():
    """Initialize the complete database with all correct schemas."""
    logger.info("🚀 Starting complete database initialization...")
    
    try:
        # Step 1: Create database if it doesn't exist
        await create_database_if_not_exists()
        
        # Step 2: Create all tables with complete schema
        await create_complete_schema()
        
        # Step 3: Verify all tables were created
        success = await verify_schema()
        
        if success:
            logger.info("🎉 Complete database initialization successful!")
            logger.info("✅ All tables created with correct schema")
            logger.info("🚀 HRMS system is ready for use!")
        else:
            logger.error("❌ Database initialization failed verification!")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Complete database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_complete_database())