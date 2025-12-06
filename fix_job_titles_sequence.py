import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

try:
    # Remove department column if it exists
    cur.execute("ALTER TABLE job_titles DROP COLUMN IF EXISTS department")
    
    # Fix the sequence for job_title_id
    cur.execute("SELECT setval('job_titles_job_title_id_seq', COALESCE(MAX(job_title_id), 0) + 1, false) FROM job_titles")
    
    conn.commit()
    print("Fixed job_titles table and sequence")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

cur.close()
conn.close()