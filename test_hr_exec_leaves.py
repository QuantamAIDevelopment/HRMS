import psycopg2

conn = psycopg2.connect(host="127.0.0.1", port="5432", database="hrms_app", user="postgres", password="Rishi@123")
cursor = conn.cursor()

print("=== Testing HR Executive Leaves ===")

# Check HR Executive employees
print("\n1. HR Executive employees:")
cursor.execute("SELECT employee_id FROM employees WHERE UPPER(designation) = 'HR EXECUTIVE'")
hr_execs = cursor.fetchall()
print(f"HR Executives found: {[emp[0] for emp in hr_execs]}")

# Check their leaves
if hr_execs:
    hr_exec_ids = [emp[0] for emp in hr_execs]
    placeholders = ','.join(['%s'] * len(hr_exec_ids))
    cursor.execute(f"SELECT employee_id, leave_type, status, start_date, end_date FROM leave_management WHERE employee_id IN ({placeholders})", hr_exec_ids)
    leaves = cursor.fetchall()
    print(f"\n2. HR Executive leaves ({len(leaves)} found):")
    for leave in leaves:
        print(f"Employee: {leave[0]}, Type: {leave[1]}, Status: {leave[2]}, Dates: {leave[3]} to {leave[4]}")
else:
    print("No HR Executives found!")

cursor.close()
conn.close()