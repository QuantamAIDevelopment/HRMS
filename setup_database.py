#!/usr/bin/env python3
"""
Standalone database setup script.
Run this script to initialize the database and create all tables.

Usage:
    python setup_database.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.database import init_database
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to set up the database."""
    logger.info("Starting database setup...")
    
    try:
        await init_database()
        logger.info("✅ Database setup completed successfully!")
        print("\n🎉 Database is ready to use!")
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        print(f"\n💥 Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("🚀 Setting up HRMS database...")
    asyncio.run(main())