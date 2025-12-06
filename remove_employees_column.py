import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

try:
    # Remove static employees column
    cur.execute("ALTER TABLE job_titles DROP COLUMN IF EXISTS employees")
    
    conn.commit()
    print("Removed static employees column from job_titles table")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

cur.close()
conn.close()