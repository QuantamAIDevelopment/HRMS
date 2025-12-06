import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

try:
    cur.execute("ALTER TABLE job_titles DROP COLUMN IF EXISTS department")
    conn.commit()
    print("Department column removed from job_titles table")
except Exception as e:
    print(f"Error: {e}")

cur.close()
conn.close()