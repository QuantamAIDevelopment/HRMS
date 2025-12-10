#!/usr/bin/env python3
"""
Test the complete database initialization script.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.scripts.complete_db_init import init_complete_database
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_complete_init():
    """Test the complete database initialization."""
    print("🧪 Testing complete database initialization...\n")
    
    try:
        await init_complete_database()
        print("\n✅ Complete database initialization test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Complete database initialization test FAILED: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_complete_init())
    if not success:
        sys.exit(1)