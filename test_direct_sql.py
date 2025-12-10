import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('src/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Test direct SQL insert without specifying user_id
    cur.execute("""
        INSERT INTO users (email, hashed_password, employee_id, role, full_name)
        VALUES ('test@example.com', 'hashedpass', 'TEST001', 'EMPLOYEE', 'Test User')
        RETURNING user_id;
    """)
    
    user_id = cur.fetchone()[0]
    print(f"User created successfully with ID: {user_id}")
    
    # Clean up
    cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    print("Test user deleted")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")