import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('src/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Make optional fields nullable
    cur.execute("ALTER TABLE employee_work_experience ALTER COLUMN experience_designation DROP NOT NULL;")
    cur.execute("ALTER TABLE employee_work_experience ALTER COLUMN company_name DROP NOT NULL;")
    cur.execute("ALTER TABLE employee_work_experience ALTER COLUMN start_date DROP NOT NULL;")
    
    conn.commit()
    print("Updated employee_work_experience table to allow NULL values")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")