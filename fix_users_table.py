import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('src/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Drop the users table
    cur.execute("DROP TABLE IF EXISTS users CASCADE;")
    conn.commit()
    print("Users table dropped successfully")
    
    # Create the users table with correct schema
    cur.execute("""
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            email VARCHAR UNIQUE,
            hashed_password VARCHAR,
            employee_id VARCHAR UNIQUE,
            role VARCHAR,
            full_name VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Verify the sequence exists and is properly linked
    cur.execute("SELECT pg_get_serial_sequence('users', 'user_id');")
    sequence = cur.fetchone()
    print(f"Sequence for user_id: {sequence[0]}")
    
    # Set the sequence to start from 1
    cur.execute("SELECT setval('users_user_id_seq', 1, false);")
    print("Sequence reset to start from 1")
    conn.commit()
    print("Users table created successfully with correct schema")
    
    cur.close()
    conn.close()
    print("Database connection closed")
    
except Exception as e:
    print(f"Error: {e}")