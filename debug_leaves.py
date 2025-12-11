import psycopg2

conn = psycopg2.connect(host="127.0.0.1", port="5432", database="hrms_app", user="postgres", password="Rishi@123")
cursor = conn.cursor()

print("=== Debugging HR Executive Leaves ===")

# Check EMP002 details
print("\n1. EMP002 details:")
cursor.execute("SELECT employee_id, first_name, last_name, designation FROM employees WHERE employee_id = 'EMP002'")
result = cursor.fetchone()
if result:
    print(f"Employee: {result[0]} - {result[1]} {result[2]} - Designation: {result[3]}")

# Check what leave tables exist
print("\n2. Available leave tables:")
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%leave%'")
tables = cursor.fetchall()
for table in tables:
    print(f"Table: {table[0]}")

# Check regular leave table
print("\n3. Regular leave management data:")
cursor.execute("SELECT COUNT(*) FROM leave_management")
count = cursor.fetchone()[0]
print(f"Total leaves in leave_management: {count}")

if count > 0:
    cursor.execute("SELECT employee_id, leave_type, status FROM leave_management LIMIT 5")
    results = cursor.fetchall()
    for row in results:
        print(f"Employee: {row[0]}, Type: {row[1]}, Status: {row[2]}")

# Check all HR employees
print("\n4. All HR employees:")
cursor.execute("SELECT employee_id, first_name, last_name, designation FROM employees WHERE LOWER(designation) LIKE '%hr%'")
results = cursor.fetchall()
for row in results:
    print(f"{row[0]} - {row[1]} {row[2]} - {row[3]}")

cursor.close()
conn.close()