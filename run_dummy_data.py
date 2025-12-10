#!/usr/bin/env python3
"""
Run script for HRMS dummy data generation
Execute this script to populate the database with test data
"""

import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Import and run the dummy data generator
from scripts.generate_dummy_data import create_dummy_data

if __name__ == "__main__":
    print("🚀 HRMS Dummy Data Generator")
    print("=" * 50)
    
    try:
        create_dummy_data()
        print("\n✅ Database populated successfully!")
        print("\n📋 Next Steps:")
        print("1. Start the HRMS server: python src/main.py")
        print("2. Import the Postman collection: HRMS_Postman_Collection.json")
        print("3. Test the APIs using the provided test credentials")
        print("\n🔗 API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check database connection in .env file")
        print("3. Run database migrations: alembic upgrade head")
        sys.exit(1)