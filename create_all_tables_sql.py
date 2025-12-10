#!/usr/bin/env python3
"""
Create all tables using raw SQL to avoid foreign key issues.
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

def create_all_tables_sql():
    """Create all tables using raw SQL."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        sql_commands = [
            # Users table
            """
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
            
            # Job titles table
            """
            CREATE TABLE IF NOT EXISTS job_titles (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                department VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,
            
            # Policy master table
            """
            CREATE TABLE IF NOT EXISTS policy_master (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                policy_type VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,
            
            # Events holidays table
            """
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
            
            # Time entries table
            """
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
            
            # Attendance table
            """
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
            
            # Leave management table
            """
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
            
            # Employee expenses table
            """
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
            
            # Payroll setup table
            """
            CREATE TABLE IF NOT EXISTS payroll_setup (
                payroll_id SERIAL PRIMARY KEY,
                employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                designation VARCHAR(100) NOT NULL,
                pay_cycle VARCHAR(20) DEFAULT 'Monthly',
                basic_salary NUMERIC(12,2) DEFAULT 0,
                hra NUMERIC(12,2) DEFAULT 0,
                allowance NUMERIC(12,2) DEFAULT 0,
                bonus_percentage NUMERIC(5,2) DEFAULT 0,
                is_bonus_taxable BOOLEAN DEFAULT FALSE,
                is_allowance_taxable BOOLEAN DEFAULT FALSE,
                is_hra_taxable BOOLEAN DEFAULT FALSE,
                is_basic_taxable BOOLEAN DEFAULT FALSE,
                provident_fund_percentage NUMERIC(5,2) DEFAULT 0,
                professional_tax NUMERIC(12,2) DEFAULT 0,
                income_tax NUMERIC(12,2) DEFAULT 0,
                lop_amount NUMERIC(12,2) DEFAULT 0,
                is_pf_locked BOOLEAN DEFAULT FALSE,
                is_pt_locked BOOLEAN DEFAULT FALSE,
                is_income_tax_auto BOOLEAN DEFAULT FALSE,
                total_earnings NUMERIC(12,2) DEFAULT 0,
                total_deductions NUMERIC(12,2) DEFAULT 0,
                net_salary NUMERIC(12,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,
            
            # Onboarding process table
            """
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
            
            # Compliance documents table
            """
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
            
            # Off boarding table
            """
            CREATE TABLE IF NOT EXISTS off_boarding (
                id SERIAL PRIMARY KEY,
                employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                reason VARCHAR(255),
                last_working_day DATE,
                status VARCHAR(50) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """
        ]
        
        with engine.connect() as conn:
            for i, sql in enumerate(sql_commands, 1):
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"✅ Created table {i}/{len(sql_commands)}")
                except Exception as e:
                    logger.warning(f"⚠️ Table {i} may already exist: {e}")
        
        logger.info("✅ All tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def main():
    """Main function."""
    print("🔨 Creating all database tables with SQL...\n")
    
    if create_all_tables_sql():
        print("\n✅ All tables created successfully!")
        
        # Verify tables
        try:
            from sqlalchemy import inspect
            sync_db_url = settings.sync_database_url
            engine = create_engine(sync_db_url)
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"\n📊 Total tables: {len(tables)}")
            for table in sorted(tables):
                print(f"  - {table}")
                
        except Exception as e:
            logger.error(f"Error verifying tables: {e}")
    else:
        print("\n❌ Failed to create tables")
        sys.exit(1)

if __name__ == "__main__":
    main()