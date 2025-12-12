#!/usr/bin/env python3
"""
Script to clean/drop all tables from the database
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent.parent)
sys.path.append(src_path)

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

os.chdir(src_path)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from models.base import Base

def clean_database():
    """Drop all tables from the database"""
    try:
        engine = create_engine(settings.database_url)
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped successfully")
        print("Database cleaned!")
        
    except Exception as e:
        print(f"Error cleaning database: {e}")

if __name__ == "__main__":
    clean_database()