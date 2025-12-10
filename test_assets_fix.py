#!/usr/bin/env python3
"""
Test that the assets model fix works.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import settings
from src.models.Employee_models import Assets
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_assets_query():
    """Test querying assets to see if the schema mismatch is fixed."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        
        # Try to query assets (this was failing before)
        assets = db.query(Assets).limit(5).all()
        
        print("✅ Assets query successful!")
        print(f"📊 Found {len(assets)} asset records")
        
        if assets:
            for asset in assets:
                print(f"📋 Asset: {asset.asset_name} ({asset.asset_type}) - Status: {asset.status}")
                if asset.assigned_employee_id:
                    print(f"   👤 Assigned to: {asset.assigned_employee_id}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Assets query failed: {e}")
        return False

def main():
    """Main function."""
    print("🧪 Testing assets model fix...\n")
    
    if test_assets_query():
        print("\n🎉 Assets model is now working correctly!")
        print("✅ The Complete Employee API should work for asset assignment")
    else:
        print("\n💥 Assets model still has issues")

if __name__ == "__main__":
    main()