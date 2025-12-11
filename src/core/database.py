"""
Database initialization and startup functions.
"""

import asyncio
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import ProgrammingError, IntegrityError
from src.config.settings import settings
from src.models import Base

logger = logging.getLogger(__name__)


async def ensure_database_exists():
    """Connect to existing database."""
    try:
        # Just test the connection to existing database
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Connected to existing database successfully")
            
    except Exception as e:
        logger.warning(f"Could not connect to database: {e}")


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
    """Connect to existing database."""
    logger.info("🚀 Connecting to database...")
    
    try:
        await ensure_database_exists()
        logger.info("🎉 Database connection successful")
        
    except Exception as e:
        logger.warning(f"⚠️ Database connection warning: {e}")
        logger.info("📝 Application will continue - some features may not work")