#!/usr/bin/env python3
"""
Script to create initial migration for employee tables
Run this after setting up the database
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command

def create_initial_migration():
    """Create initial migration for employee tables"""
    
    # Get the alembic.ini path
    alembic_cfg_path = Path(__file__).parent.parent.parent / "alembic.ini"
    
    if not alembic_cfg_path.exists():
        print(f"Error: alembic.ini not found at {alembic_cfg_path}")
        return
    
    # Create alembic config
    alembic_cfg = Config(str(alembic_cfg_path))
    
    try:
        # Create initial migration
        command.revision(
            alembic_cfg, 
            autogenerate=True, 
            message="Initial migration - employee tables"
        )
        print("✅ Initial migration created successfully!")
        print("Run 'alembic upgrade head' to apply the migration")
        
    except Exception as e:
        print(f"❌ Error creating migration: {e}")

if __name__ == "__main__":
    create_initial_migration()