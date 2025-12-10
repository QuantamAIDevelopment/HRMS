import psycopg2
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # List all tables
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"))
        tables = result.fetchall()
        
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Check specific table names your app is looking for
        check_tables = ['users', 'userss', 'employees', 'departments']
        for table_name in check_tables:
            result = conn.execute(text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}');"))
            exists = result.fetchone()[0]
            print(f"{table_name}: {'EXISTS' if exists else 'NOT FOUND'}")
            
except Exception as e:
    print(f"Error: {e}")