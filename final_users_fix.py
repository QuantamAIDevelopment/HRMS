import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('src/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Drop everything related to users
    cur.execute("DROP TABLE IF EXISTS users CASCADE;")
    cur.execute("DROP SEQUENCE IF EXISTS users_user_id_seq CASCADE;")
    cur.execute("DROP SEQUENCE IF EXISTS users_user_id_seq1 CASCADE;")
    cur.execute("DROP SEQUENCE IF EXISTS userss_user_id_seq CASCADE;")
    
    # Create table with SERIAL - this automatically creates the sequence
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
    
    # Test that it works
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
    print("Test record cleaned up")
    
    # Check the sequence name
    cur.execute("SELECT pg_get_serial_sequence('users', 'user_id');")
    seq_name = cur.fetchone()[0]
    print(f"Sequence name: {seq_name}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")