import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

try:
    # Insert sample job titles
    sample_data = [
        ("Software Engineer", "Develops and maintains software applications", "IT", 30000, 60000),
        ("Senior Developer", "Leads development projects and mentors junior developers", "IT", 50000, 90000),
        ("HR Manager", "Manages HR operations and employee relations", "HR", 40000, 75000),
        ("Sales Executive", "Handles client relationships and sales targets", "Sales", 25000, 50000),
        ("Project Manager", "Oversees project planning and execution", "IT", 45000, 85000)
    ]
    
    for job_title, description, department, min_sal, max_sal in sample_data:
        cur.execute("""
            INSERT INTO job_titles (job_title, job_description, department, salary_min, salary_max)
            VALUES (%s, %s, %s, %s, %s)
        """, (job_title, description, department, min_sal, max_sal))
    
    conn.commit()
    print("Sample job titles added successfully")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

cur.close()
conn.close()