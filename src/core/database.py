"""
Database initialization and startup functions.
"""

import asyncio
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import ProgrammingError, IntegrityError
from config.settings import settings
from models import Base

logger = logging.getLogger(__name__)


async def ensure_database_exists():
    """Ensure the database exists, create if it doesn't."""
    try:
        db_url = settings.database_url
        db_name = db_url.split('/')[-1]
        
        # Create connection to postgres database
        postgres_url = db_url.rsplit('/', 1)[0] + '/postgres'
        sync_postgres_url = postgres_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_postgres_url)
        
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            if not result.fetchone():
                conn.execute(text("COMMIT"))
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Created database: {db_name}")
            
    except Exception as e:
        logger.warning(f"Could not create database: {e}")


async def create_tables():
    """Create all tables if they don't exist."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        # Check existing tables first
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        logger.info(f"Found {len(existing_tables)} existing tables: {existing_tables}")
        
        # Force create all tables from Base metadata
        logger.info(f"Expected tables from models: {list(Base.metadata.tables.keys())}")
        
        # Always try to create tables - SQLAlchemy will skip existing ones
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        # Check again after creation
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        logger.info(f"After creation: {len(new_tables)} tables exist: {new_tables}")
        
        if len(new_tables) > len(existing_tables):
            logger.info(f"Successfully created {len(new_tables) - len(existing_tables)} new tables")
        else:
            logger.info("All expected tables already existed")
        
    except Exception as e:
        # Log the error but don't raise it - the app should still start
        logger.warning(f"Database initialization completed with warnings: {e}")
        logger.info("Application will continue - database may need manual setup")


async def init_database():
    """Initialize database on startup with complete schema."""
    logger.info("🚀 Initializing database...")
    
    try:
        await ensure_database_exists()
        
        # Check if tables exist
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
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
        else:
            logger.info(f"🔨 Creating {len(missing_tables)} missing tables with complete schema...")
            # Use the complete database initialization
            from scripts.complete_db_init import create_complete_schema
            await create_complete_schema()
        
        logger.info("🎉 Database initialization complete")
        
    except Exception as e:
        logger.warning(f"⚠️ Database initialization warning: {e}")
        logger.info("📝 Application will continue - some features may not work")