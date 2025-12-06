import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

try:
    cur.execute("ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS department VARCHAR(30) NOT NULL DEFAULT 'General'")
    conn.commit()
    print("Department column added to job_titles table")
except Exception as e:
    print(f"Error: {e}")

cur.close()
conn.close()