import psycopg2
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Testing connection to: {DATABASE_URL}")

try:
    # Test connection
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database();"))
        db_name = result.fetchone()[0]
        print(f"Connected to database: {db_name}")
        
        # Check if users table exists
        result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');"))
        users_exists = result.fetchone()[0]
        print(f"Users table exists: {users_exists}")
        
        if not users_exists:
            print("Tables don't exist. You need to run the SQL script to create them.")
        else:
            print("Tables exist.")
            
except Exception as e:
    print(f"Connection failed: {e}")