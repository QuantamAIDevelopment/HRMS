import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

try:
    # Create leave_management table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leave_management (
            leave_id SERIAL PRIMARY KEY,
            employee_id VARCHAR(50) NOT NULL,
            leave_type VARCHAR(50) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            reason TEXT,
            status VARCHAR(20) DEFAULT 'PENDING',
            applied_date DATE DEFAULT CURRENT_DATE,
            approved_by VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Insert sample leave data
    cur.execute("""
        INSERT INTO leave_management (employee_id, leave_type, start_date, end_date, reason, status)
        VALUES 
        ('EMP001', 'Sick Leave', '2024-12-05', '2024-12-06', 'Medical appointment', 'APPROVED'),
        ('EMP002', 'Annual Leave', '2024-12-10', '2024-12-12', 'Personal work', 'APPROVED')
        ON CONFLICT DO NOTHING
    """)
    
    conn.commit()
    print("Leave management table created successfully")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

cur.close()
conn.close()