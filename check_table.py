import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('src/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check table structure
    cur.execute("""
        SELECT column_name, data_type, column_default, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'users'
        ORDER BY ordinal_position;
    """)
    
    columns = cur.fetchall()
    print("Current users table structure:")
    for col in columns:
        print(f"  {col[0]}: {col[1]} (default: {col[2]}, nullable: {col[3]})")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")