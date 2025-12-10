import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('src/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'employee_work_experience'
        );
    """)
    
    table_exists = cur.fetchone()[0]
    print(f"employee_work_experience table exists: {table_exists}")
    
    if table_exists:
        # Check table structure
        cur.execute("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'employee_work_experience'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        print("Table structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} (default: {col[2]}, nullable: {col[3]})")
    else:
        print("Table does not exist - creating it")
        cur.execute("""
            CREATE TABLE employee_work_experience (
                experience_id SERIAL PRIMARY KEY,
                employee_id VARCHAR(50) REFERENCES employees(employee_id) ON DELETE CASCADE,
                experience_designation VARCHAR(150),
                company_name VARCHAR(200),
                start_date DATE,
                end_date DATE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("Table created successfully")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")