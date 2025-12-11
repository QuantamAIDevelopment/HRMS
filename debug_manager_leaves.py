import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

# Create database connection using direct URL
DATABASE_URL = "postgresql://postgres:Rishi%40123@127.0.0.1:5432/hrms_app"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check EMP004 designation
    result = conn.execute(text("SELECT employee_id, designation FROM employees WHERE employee_id = 'EMP004'"))
    emp004 = result.fetchone()
    print(f"EMP004 details: {emp004}")
    
    # Check all employees with manager designation
    result = conn.execute(text("SELECT employee_id, designation FROM employees WHERE UPPER(designation) LIKE '%MANAGER%' AND UPPER(designation) NOT LIKE '%HR MANAGER%'"))
    managers = result.fetchall()
    print(f"Managers found: {managers}")
    
    # Check the exact query from the service
    result = conn.execute(text("SELECT employee_id, designation FROM employees WHERE designation = 'HR Executive'"))
    hr_execs = result.fetchall()
    print(f"HR Executives (exact match): {hr_execs}")
    
    result = conn.execute(text("SELECT employee_id, designation FROM employees WHERE LOWER(designation) LIKE '%hr executive%'"))
    hr_execs_like = result.fetchall()
    print(f"HR Executives (like match): {hr_execs_like}")
    
    # Check all leaves in the system
    result = conn.execute(text("SELECT COUNT(*) FROM leave_management"))
    total_leaves = result.fetchone()[0]
    print(f"Total leaves in database: {total_leaves}")
    
    # Check manager leaves specifically
    result = conn.execute(text("""
        SELECT l.leave_id, l.employee_id, l.leave_type, l.status, e.designation
        FROM leave_management l 
        JOIN employees e ON l.employee_id = e.employee_id 
        WHERE UPPER(e.designation) LIKE '%MANAGER%' AND UPPER(e.designation) NOT LIKE '%HR MANAGER%'
    """))
    manager_leaves = result.fetchall()
    print(f"Manager leaves found: {manager_leaves}")