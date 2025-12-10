import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('src/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Drop and recreate with explicit DEFAULT
    cur.execute("DROP TABLE IF EXISTS users CASCADE;")
    
    cur.execute("""
        CREATE TABLE users (
            user_id INTEGER NOT NULL DEFAULT nextval('users_user_id_seq'::regclass) PRIMARY KEY,
            email VARCHAR UNIQUE,
            hashed_password VARCHAR,
            employee_id VARCHAR UNIQUE,
            role VARCHAR,
            full_name VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create the sequence if it doesn't exist
    cur.execute("CREATE SEQUENCE IF NOT EXISTS users_user_id_seq OWNED BY users.user_id;")
    
    conn.commit()
    print("Users table recreated with explicit DEFAULT")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")