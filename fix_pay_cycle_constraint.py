import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="hrms_db", 
    user="postgres",
    password="psycho539"
)

cur = conn.cursor()

try:
    # Check current constraint
    cur.execute("""
        SELECT conname, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'payroll_setup'::regclass AND conname = 'check_pay_cycle';
    """)
    
    result = cur.fetchone()
    if result:
        print(f"Current constraint: {result[1]}")
    
    # Drop and recreate constraint to allow lowercase
    cur.execute("ALTER TABLE payroll_setup DROP CONSTRAINT IF EXISTS check_pay_cycle;")
    cur.execute("""
        ALTER TABLE payroll_setup ADD CONSTRAINT check_pay_cycle 
        CHECK (pay_cycle IN ('Monthly','Weekly','Biweekly','monthly','weekly','biweekly'));
    """)
    
    conn.commit()
    print("SUCCESS: pay_cycle constraint updated to allow lowercase values")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()