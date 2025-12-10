import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.session import get_db
from models.user import User
from core.security import get_password_hash

# Test user creation
db = next(get_db())

try:
    # Create a test user
    test_user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        employee_id="TEST001",
        role="EMPLOYEE",
        full_name="Test User"
    )
    
    db.add(test_user)
    db.commit()
    print(f"User created successfully with ID: {test_user.user_id}")
    
    # Clean up
    db.delete(test_user)
    db.commit()
    print("Test user deleted")
    
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()