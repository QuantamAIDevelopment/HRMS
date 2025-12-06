import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

try:
    # Check if table exists and its structure
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'leave_management'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    print("Leave management table columns:")
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
    
    # Check sample data
    cur.execute("SELECT * FROM leave_management LIMIT 5")
    data = cur.fetchall()
    print(f"\nSample data ({len(data)} rows):")
    for row in data:
        print(f"  {row}")
        
except Exception as e:
    print(f"Error: {e}")

cur.close()
conn.close()