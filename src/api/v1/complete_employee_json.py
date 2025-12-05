from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.deps import get_db
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()

class EmployeeCreateJSON(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email_id: str
    employee_phone: str
    date_of_birth: str
    gender: str
    blood_group: str
    marital_status: str
    nationality: str
    employee_email: str
    employee_address: str
    emergency_full_name: str
    emergency_relationship: str
    emergency_primary_phone: str
    emergency_address: str
    designation: str
    department_id: str
    joining_date: str
    employment_type: str
    account_number: str
    account_holder_name: str
    ifsc_code: str
    bank_name: str
    branch: str
    account_type: str
    pan_number: str
    aadhaar_number: str
    
    # Optional fields
    employee_alternate_phone: Optional[str] = None
    emergency_alternate_phone: Optional[str] = None
    reporting_manager: Optional[str] = None
    location: Optional[str] = None

@router.post("/complete-employee-json")
def create_employee_json(
    employee_data: EmployeeCreateJSON,
    db: Session = Depends(get_db)
):
    try:
        from src.models.Employee_models import Employee, EmployeePersonalDetails, BankDetails
        
        # Create Employee
        employee = Employee(
            employee_id=employee_data.employee_id,
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            department_id=int(employee_data.department_id),
            designation=employee_data.designation,
            joining_date=datetime.strptime(employee_data.joining_date, "%Y-%m-%d").date(),
            reporting_manager=employee_data.reporting_manager or "TBD",
            email_id=employee_data.email_id,
            phone_number=employee_data.employee_phone,
            location=employee_data.location or "Office",
            shift_id=1,
            employment_type=employee_data.employment_type,
            status="active"
        )
        db.add(employee)
        
        # Create Personal Details
        personal = EmployeePersonalDetails(
            employee_id=employee_data.employee_id,
            date_of_birth=datetime.strptime(employee_data.date_of_birth, "%Y-%m-%d").date(),
            gender=employee_data.gender,
            marital_status=employee_data.marital_status,
            blood_group=employee_data.blood_group,
            nationality=employee_data.nationality,
            employee_phone=employee_data.employee_phone,
            employee_email=employee_data.employee_email,
            employee_alternate_phone=employee_data.employee_alternate_phone,
            employee_address=employee_data.employee_address,
            emergency_full_name=employee_data.emergency_full_name,
            emergency_relationship=employee_data.emergency_relationship,
            emergency_primary_phone=employee_data.emergency_primary_phone,
            emergency_alternate_phone=employee_data.emergency_alternate_phone,
            emergency_address=employee_data.emergency_address
        )
        db.add(personal)
        
        # Create Bank Details
        bank = BankDetails(
            employee_id=employee_data.employee_id,
            account_number=employee_data.account_number,
            account_holder_name=employee_data.account_holder_name,
            ifsc_code=employee_data.ifsc_code,
            bank_name=employee_data.bank_name,
            branch=employee_data.branch,
            account_type=employee_data.account_type,
            pan_number=employee_data.pan_number,
            aadhaar_number=employee_data.aadhaar_number
        )
        db.add(bank)
        
        db.commit()
        
        return {"message": "Employee created successfully", "employee_id": employee_data.employee_id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))