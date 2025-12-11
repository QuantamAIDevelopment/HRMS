import psycopg2

conn = psycopg2.connect(host="127.0.0.1", port="5432", database="hrms_app", user="postgres", password="Rishi@123")
cursor = conn.cursor()

print("=== Assets Table Structure ===")
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'assets' ORDER BY ordinal_position")
columns = cursor.fetchall()

for col in columns:
    print(f"Column: {col[0]} - Type: {col[1]}")

cursor.close()
conn.close()