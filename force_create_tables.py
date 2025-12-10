#!/usr/bin/env python3
"""
Force create all database tables.
This script will explicitly import all models and create tables.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, inspect
from src.config.settings import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_all_models():
    """Import all model files to ensure they're registered with Base."""
    try:
        # Import base first
        from src.models.base import Base
        
        # Import models in dependency order (parent tables first)
        from src.models import user
        from src.models import job_title
        from src.models import shift
        from src.models import policy
        
        # Import Employee_models first (contains employees table)
        from src.models import Employee_models
        
        # Then import models that depend on employees
        from src.models import hrms_models
        from src.models import timesheet
        from src.models import off_boarding
        from src.models import events_holidays
        from src.models import leave
        
        logger.info("All model files imported successfully")
        return Base
        
    except Exception as e:
        logger.error(f"Error importing models: {e}")
        raise

def create_all_tables():
    """Force create all tables."""
    try:
        # Import all models first
        Base = import_all_models()
        
        # Show what tables we expect to create
        expected_tables = list(Base.metadata.tables.keys())
        logger.info(f"Expected to create {len(expected_tables)} tables:")
        for table in expected_tables:
            logger.info(f"  - {table}")
        
        # Create engine
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        # Check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info(f"Existing tables: {existing_tables}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Table creation completed")
        
        # Check what was created
        inspector = inspect(engine)
        final_tables = inspector.get_table_names()
        logger.info(f"Final table count: {len(final_tables)}")
        logger.info(f"Tables now in database: {final_tables}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def main():
    """Main function."""
    print("🔨 Force creating all database tables...\n")
    
    success = create_all_tables()
    
    if success:
        print("\n✅ All tables created successfully!")
    else:
        print("\n❌ Failed to create tables")
        sys.exit(1)

if __name__ == "__main__":
    main()