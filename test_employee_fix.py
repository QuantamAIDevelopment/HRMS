import sys
sys.path.append('src')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Import from the main models file only
from models.hrms_models import Employee, EmployeePersonalDetails
from datetime import date

# Database connection
engine = create_engine("postgresql://postgres:psycho539@localhost:5432/hrms_db")
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Test employee creation
    emp = Employee(
        employee_id="TEST002", 
        first_name="Test", 
        last_name="User",
        department_id=1, 
        designation="Test Engineer", 
        joining_date=date(2025, 1, 1),
        email_id="test2@test.com", 
        phone_number="1234567890", 
        shift_id=1, 
        employee_type="Full-time"
    )
    session.add(emp)
    session.flush()  # This should work now
    print("SUCCESS: Employee created and flushed")
    
    # Test personal details creation
    personal = EmployeePersonalDetails(
        employee_id=emp.employee_id,
        date_of_birth=date(1990, 1, 1),
        gender="Male"
    )
    session.add(personal)
    session.flush()
    print("SUCCESS: Personal details created and flushed")
    
    # Test relationship
    print(f"Employee personal details: {emp.personal_details}")
    print("SUCCESS: Relationship working")
    
    session.rollback()  # Don't save test data
    
except Exception as e:
    print(f"ERROR: {e}")
    session.rollback()
finally:
    session.close()