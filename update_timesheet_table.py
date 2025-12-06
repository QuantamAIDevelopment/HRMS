import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

try:
    # Add new columns for approval hierarchy
    cur.execute("ALTER TABLE time_entries ADD COLUMN IF NOT EXISTS approver_id VARCHAR(50)")
    cur.execute("ALTER TABLE time_entries ADD COLUMN IF NOT EXISTS approver_type VARCHAR(20)")
    
    # Update existing records
    cur.execute("UPDATE time_entries SET status = 'PENDING_MANAGER_APPROVAL' WHERE status = 'PENDING'")
    
    conn.commit()
    print("Timesheet table updated with approval hierarchy")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

cur.close()
conn.close()