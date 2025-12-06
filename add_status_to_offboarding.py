import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

try:
    # Add status column to off_boarding table
    cur.execute("ALTER TABLE off_boarding ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'PENDING'")
    
    conn.commit()
    print("Status column added to off_boarding table")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

cur.close()
conn.close()