import psycopg2
from psycopg2 import sql

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="hrms_db", 
    user="postgres",
    password="psycho539"
)

cur = conn.cursor()

# SQL commands to add missing columns
sql_commands = [
    "ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS pdf_path VARCHAR(255);",
    "ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS month VARCHAR(20);",
    "ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS basic_salary_type VARCHAR(50);",
    "ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS hra_type VARCHAR(50);",
    "ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS allowance_type VARCHAR(50);",
    "ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS provident_fund_type VARCHAR(50);",
    "ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS professional_tax_type VARCHAR(50);",
    "ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS salary_components JSONB;",
    "ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS organization_name VARCHAR(100);",
    "CREATE INDEX IF NOT EXISTS idx_payroll_month ON payroll_setup(month);",
    "CREATE INDEX IF NOT EXISTS idx_payroll_employee_id ON payroll_setup(employee_id);",
    "CREATE INDEX IF NOT EXISTS idx_employee_month ON payroll_setup(employee_id, month);"
]

try:
    for cmd in sql_commands:
        print(f"Executing: {cmd}")
        cur.execute(cmd)
    
    conn.commit()
    print("✅ All columns added successfully!")
    
    # Verify columns exist
    cur.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'payroll_setup' 
        ORDER BY ordinal_position;
    """)
    
    print("\n📋 Current payroll_setup table structure:")
    for row in cur.fetchall():
        print(f"  {row[0]} | {row[1]} | nullable: {row[2]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()