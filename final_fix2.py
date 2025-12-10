import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('src/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Drop table and sequence
    cur.execute("DROP TABLE IF EXISTS users CASCADE;")
    cur.execute("DROP SEQUENCE IF EXISTS users_user_id_seq CASCADE;")
    
    # Create sequence first
    cur.execute("CREATE SEQUENCE users_user_id_seq;")
    
    # Create table with SERIAL (which creates its own sequence)
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
    
    conn.commit()
    print("Users table recreated with SERIAL")
    
    # Test insert
    cur.execute("""
        INSERT INTO users (email, hashed_password, employee_id, role, full_name)
        VALUES ('test@example.com', 'hash', 'TEST001', 'EMPLOYEE', 'Test User')
        RETURNING user_id;
    """)
    user_id = cur.fetchone()[0]
    print(f"Test insert successful, user_id: {user_id}")
    
    # Clean up test
    cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")