import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

try:
    # Drop existing table and recreate with new structure
    cur.execute("DROP TABLE IF EXISTS job_titles CASCADE")
    
    # Create new table with exact structure
    cur.execute("""
        CREATE TABLE job_titles (
            job_title_id SERIAL PRIMARY KEY,
            job_title VARCHAR(100) NOT NULL,
            job_description VARCHAR(255),
            department VARCHAR(30) NOT NULL,
            salary_min INTEGER,
            salary_max INTEGER,
            employees INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    conn.commit()
    print("Job titles table recreated with new structure")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

cur.close()
conn.close()