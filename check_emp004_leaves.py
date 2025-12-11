import psycopg2

conn = psycopg2.connect(host="127.0.0.1", port="5432", database="hrms_app", user="postgres", password="Rishi@123")
cursor = conn.cursor()

print("=== EMP004 Leave Details ===")
cursor.execute("SELECT leave_type, status FROM leave_management WHERE employee_id = 'EMP004' ORDER BY leave_id DESC")
leaves = cursor.fetchall()

print("All leaves:")
for leave in leaves:
    print(f"Type: '{leave[0]}' - Status: {leave[1]}")

print("\nApproved leaves by type:")
cursor.execute("SELECT leave_type, COUNT(*) FROM leave_management WHERE employee_id = 'EMP004' AND status = 'APPROVED' GROUP BY leave_type")
approved = cursor.fetchall()
for leave in approved:
    print(f"Type: '{leave[0]}' - Count: {leave[1]}")

cursor.close()
conn.close()