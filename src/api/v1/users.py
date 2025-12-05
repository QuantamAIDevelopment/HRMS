from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.models.user import User
from src.models.Employee_models import Employee

from src.core.security import get_password_hash
from src.services.email_service import send_otp_email
import random
import string

router = APIRouter()

# Moved to UserService - keeping for backward compatibility
def generate_dummy_password(length=8):
    """Generate a random password - deprecated, use UserService.generate_temp_password"""
    characters = string.ascii_letters + string.digits + "@#$"
    return ''.join(random.choice(characters) for _ in range(length))

@router.get("/users")
def get_users():
    return {"message": "Get users endpoint"}

@router.post("/test-user-validation")
def test_user_validation(
    employee_id: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # ONLY check if employee_id exists in employees table
        employee = db.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()
        if not employee:
            return {"message": "Employee ID not found. Complete onboarding first.", "status": "error"}
        
        return {
            "message": "Employee ID found successfully", 
            "employee_id": employee.employee_id,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "status": "success"
        }
    except Exception as e:
        return {"message": f"Error: {str(e)}", "status": "error"}

@router.post("/users")
def create_user(
    employee_id: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    from src.services.user_service import UserService
    
    try:
        # Check if user already exists with this email
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return {"message": "User with this email already exists"}
        
        # ONLY check if employee_id exists in employees table
        employee = db.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()
        if not employee:
            return {"message": "Employee not found with provided ID. Complete onboarding first."}
        
        # Create user with temporary password (1-hour expiry)
        full_name = f"{employee.first_name} {employee.last_name}" if employee.first_name and employee.last_name else "Employee"
        role = employee.designation if employee.designation else "EMPLOYEE"
        
        new_user, temp_password = UserService.create_user_with_temp_password(
            db=db,
            employee_id=employee_id,
            email=email,
            full_name=full_name,
            role=role
        )
        
        return {
            "message": "User created successfully with temporary password (valid for 1 hour)",
            "employee_id": employee_id,
            "email": email,
            "full_name": full_name,
            "role": role,
            "temp_password_expires_in": "1 hour",
            "status": "Account created and credentials sent via email"
        }
        
    except Exception as e:
        db.rollback()
        return {"message": f"Error: {str(e)}"}