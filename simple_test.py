import sys
sys.path.append('src')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.hrms_models import Employee, EmployeePersonalDetails
from datetime import date

engine = create_engine("postgresql://postgres:psycho539@localhost:5432/hrms_db")
Session = sessionmaker(bind=engine)
session = Session()

try:
    emp = Employee(
        employee_id="TEST004", 
        first_name="Test", 
        last_name="User",
        department_id=1, 
        designation="Test Engineer", 
        joining_date=date(2025, 1, 1),
        email_id="test4@test.com", 
        phone_number="1234567890", 
        shift_id=1, 
        employee_type="Full-time"
    )
    session.add(emp)
    session.flush()
    print("SUCCESS: Employee flush works!")
    
    personal = EmployeePersonalDetails(
        employee_id=emp.employee_id,
        date_of_birth=date(1990, 1, 1),
        gender="Male"
    )
    session.add(personal)
    session.flush()
    print("SUCCESS: Personal details flush works!")
    print("FIXED: UnmappedColumnError resolved!")
    
    session.rollback()
    
except Exception as e:
    print(f"ERROR: {e}")
    session.rollback()
finally:
    session.close()