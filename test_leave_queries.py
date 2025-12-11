import psycopg2

conn = psycopg2.connect(host="127.0.0.1", port="5432", database="hrms_app", user="postgres", password="Rishi@123")
cursor = conn.cursor()

print("=== Testing Leave Queries ===")

# Test exact queries used in the API
casual_used = cursor.execute("SELECT COUNT(*) FROM leave_management WHERE employee_id = 'EMP004' AND status = 'APPROVED' AND LOWER(leave_type) = 'casual'")
casual_count = cursor.fetchone()[0]
print(f"Casual used: {casual_count}")

sick_used = cursor.execute("SELECT COUNT(*) FROM leave_management WHERE employee_id = 'EMP004' AND status = 'APPROVED' AND LOWER(leave_type) = 'sick'")
sick_count = cursor.fetchone()[0]
print(f"Sick used: {sick_count}")

earned_used = cursor.execute("SELECT COUNT(*) FROM leave_management WHERE employee_id = 'EMP004' AND status = 'APPROVED' AND LOWER(leave_type) = 'earned'")
earned_count = cursor.fetchone()[0]
print(f"Earned used: {earned_count}")

cursor.close()
conn.close()