import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="hrms_db", 
    user="postgres",
    password="psycho539"
)

cur = conn.cursor()

try:
    # Check if pdf_path column exists
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'payroll_setup' AND column_name = 'pdf_path';
    """)
    
    result = cur.fetchone()
    if result:
        print("SUCCESS: pdf_path column exists!")
        print(f"Column: {result[0]}, Type: {result[1]}")
    else:
        print("ERROR: pdf_path column still missing!")
    
    # Show all columns
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'payroll_setup' 
        ORDER BY ordinal_position;
    """)
    
    print("\nAll payroll_setup columns:")
    for row in cur.fetchall():
        print(f"  - {row[0]}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    cur.close()
    conn.close()