import sys
sys.path.append('src')

from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker
from models.hrms_models import Employee, EmployeePersonalDetails
from models.base import Base

# Database connection
engine = create_engine("postgresql://postgres:psycho539@localhost:5432/hrms_db")
Session = sessionmaker(bind=engine)
session = Session()

print("=== DIAGNOSTIC RESULTS ===")

try:
    # 1. Check mapper columns
    mapper = inspect(Employee)
    print(f"Employee columns: {[col.key for col in mapper.columns]}")
    
    # 2. Verify PK
    print(f"Employee PK: {[col.key for col in mapper.primary_key]}")
    
    # 3. Test creation
    emp = Employee(employee_id="TEST001", first_name="Test", last_name="User", 
                   department_id=1, designation="Test", joining_date="2025-01-01",
                   email_id="test@test.com", phone_number="1234567890", 
                   shift_id=1, employee_type="Full-time")
    session.add(emp)
    session.flush()
    print("✓ Employee creation successful")
    
    # 4. Check relationship
    if hasattr(Employee, 'personal_details'):
        rel_prop = Employee.personal_details.property
        print(f"Relationship foreign_keys: {rel_prop.foreign_keys}")
    else:
        print("✗ No personal_details relationship found")
    
    # 5. Validate FK join
    result = session.query(Employee).join(EmployeePersonalDetails, isouter=True).first()
    print("✓ FK join successful")
    
    session.rollback()  # Don't save test data
    
except Exception as e:
    print(f"✗ Error: {e}")
    session.rollback()

finally:
    session.close()