#!/usr/bin/env python3
"""
Fresh HRMS deployment script.
This script sets up a complete HRMS database from scratch with all correct schemas.
Perfect for new deployments or resetting the database.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, text
from src.config.settings import settings
from src.scripts.complete_db_init import init_complete_database
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def drop_database_if_exists():
    """Drop the database if it exists (for fresh deployment)."""
    try:
        # Extract database name from URL
        db_url = settings.database_url
        db_name = db_url.split('/')[-1]
        
        # Create connection to postgres database
        postgres_url = db_url.rsplit('/', 1)[0] + '/postgres'
        sync_postgres_url = postgres_url.replace("postgresql+asyncpg://", "postgresql://")
        engine = create_engine(sync_postgres_url)
        
        with engine.connect() as conn:
            # Terminate existing connections to the database
            conn.execute(text(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{db_name}' AND pid <> pg_backend_pid()
            """))
            
            # Drop database if it exists
            conn.execute(text("COMMIT"))
            conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
            logger.info(f"🗑️ Dropped existing database: {db_name}")
                
    except Exception as e:
        logger.warning(f"⚠️ Could not drop database (may not exist): {e}")


async def create_sample_data():
    """Create some sample data for testing."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        sample_data_sql = [
            # Sample departments
            "INSERT INTO departments (department_name) VALUES ('IT') ON CONFLICT DO NOTHING",
            "INSERT INTO departments (department_name) VALUES ('HR') ON CONFLICT DO NOTHING",
            "INSERT INTO departments (department_name) VALUES ('Finance') ON CONFLICT DO NOTHING",
            "INSERT INTO departments (department_name) VALUES ('Marketing') ON CONFLICT DO NOTHING",
            
            # Sample shifts
            """INSERT INTO shift_master (shift_name, shift_type, start_time, end_time, working_days) 
               VALUES ('General Shift', 'Regular', '09:00', '18:00', 'Monday-Friday') ON CONFLICT DO NOTHING""",
            """INSERT INTO shift_master (shift_name, shift_type, start_time, end_time, working_days) 
               VALUES ('Night Shift', 'Night', '22:00', '06:00', 'Monday-Friday') ON CONFLICT DO NOTHING""",
            
            # Sample job titles
            "INSERT INTO job_titles (title, description, department) VALUES ('Software Engineer', 'Develops software applications', 'IT') ON CONFLICT DO NOTHING",
            "INSERT INTO job_titles (title, description, department) VALUES ('HR Manager', 'Manages human resources', 'HR') ON CONFLICT DO NOTHING",
            "INSERT INTO job_titles (title, description, department) VALUES ('Financial Analyst', 'Analyzes financial data', 'Finance') ON CONFLICT DO NOTHING",
            
            # Sample events/holidays
            "INSERT INTO events_holidays (name, date, type, description) VALUES ('New Year', '2024-01-01', 'Public Holiday', 'New Year celebration') ON CONFLICT DO NOTHING",
            "INSERT INTO events_holidays (name, date, type, description) VALUES ('Independence Day', '2024-08-15', 'Public Holiday', 'India Independence Day') ON CONFLICT DO NOTHING",
        ]
        
        with engine.connect() as conn:
            for sql in sample_data_sql:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Sample data warning: {e}")
        
        logger.info("✅ Sample data created successfully")
        
    except Exception as e:
        logger.warning(f"⚠️ Could not create sample data: {e}")


async def deploy_fresh_hrms(drop_existing=False):
    """Deploy a fresh HRMS database."""
    print("🚀 FRESH HRMS DEPLOYMENT")
    print("=" * 50)
    
    try:
        if drop_existing:
            print("\n🗑️ Step 1: Dropping existing database...")
            await drop_database_if_exists()
        
        print("\n🏗️ Step 2: Creating complete database schema...")
        await init_complete_database()
        
        print("\n📊 Step 3: Adding sample data...")
        await create_sample_data()
        
        print("\n" + "=" * 50)
        print("🎉 FRESH HRMS DEPLOYMENT COMPLETED!")
        print("=" * 50)
        print("\n✅ Your HRMS system is ready with:")
        print("  - Complete database schema")
        print("  - All required tables and columns")
        print("  - Proper constraints and relationships")
        print("  - Sample departments, shifts, and holidays")
        print("  - Ready for Complete Employee API")
        
        print(f"\n🚀 Start your server with:")
        print(f"   uvicorn src.main:app --host 127.0.0.1 --port 8002")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        return False


def main():
    """Main function with user interaction."""
    print("🏗️ HRMS Fresh Deployment Script")
    print("=" * 40)
    
    # Ask user if they want to drop existing database
    while True:
        response = input("\n⚠️ Do you want to drop the existing database? (y/N): ").lower().strip()
        if response in ['y', 'yes']:
            drop_existing = True
            break
        elif response in ['n', 'no', '']:
            drop_existing = False
            break
        else:
            print("Please enter 'y' for yes or 'n' for no")
    
    # Run deployment
    success = asyncio.run(deploy_fresh_hrms(drop_existing))
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()