from src.config.settings import settings
from src.models.session import engine
import os
from dotenv import load_dotenv

load_dotenv()

print(f"Environment DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"Settings DATABASE_URL: {settings.DATABASE_URL}")
print(f"Engine URL: {engine.url}")

# Test connection
try:
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database();"))
        db_name = result.fetchone()[0]
        print(f"Connected to database: {db_name}")
        
        # Check if users table exists
        result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');"))
        users_exists = result.fetchone()[0]
        print(f"Users table exists: {users_exists}")
        
except Exception as e:
    print(f"Connection error: {e}")