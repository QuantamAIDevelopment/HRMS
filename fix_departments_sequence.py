import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="hrms_db", 
    user="postgres",
    password="psycho539"
)

cur = conn.cursor()

try:
    # Check current max ID and sequence value
    cur.execute("SELECT MAX(department_id) FROM departments;")
    max_id = cur.fetchone()[0] or 0
    print(f"Max department_id in table: {max_id}")
    
    cur.execute("SELECT last_value, is_called FROM departments_department_id_seq;")
    seq_info = cur.fetchone()
    print(f"Sequence last_value: {seq_info[0]}, is_called: {seq_info[1]}")
    
    # Fix sequence
    cur.execute("SELECT setval('departments_department_id_seq', %s);", (max_id,))
    new_val = cur.fetchone()[0]
    print(f"Sequence updated to: {new_val}")
    
    conn.commit()
    print("SUCCESS: departments sequence fixed")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()