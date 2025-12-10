from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from fastapi import Query
import json



from src.models.session import get_db
from src.models.Employee_models import EmployeeWorkExperience
from src.models.employee_profile import ProfileEditRequest
from src.models import Employee
from src.models.Employee_models import BankDetails, EmployeeDocuments as EmployeeDocument
from src.models.Employee_models import EmployeePersonalDetailsModel as EmployeePersonalDetails
from src.models.Employee_models import Assets as Asset
from src.schemas.profile import ProfileEditRequestCreate

router = APIRouter()

@router.post("/employees/{employee_id}/request-basic-edit")
def request_basic_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Basic info edit request submitted"}

@router.post("/employees/{employee_id}/request-personal-edit")
def request_personal_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Personal details edit request submitted"}

@router.post("/employees/{employee_id}/request-bank-edit")
def request_bank_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Bank details edit request submitted"}

@router.post("/employees/{employee_id}/request-experience-edit")
def request_experience_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Work experience edit request submitted"}

@router.post("/employees/{employee_id}/request-document-edit")
def request_document_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Document edit request submitted"}

@router.post("/employees/{employee_id}/request-assets-edit")
def request_assets_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Assets edit request submitted"}

@router.get("/employees/{employee_id}")
def get_employee_complete(employee_id: str, db: Session = Depends(get_db)):
    from src.models import Department, ShiftMaster
    
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    personal_details = db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
    bank_details = db.query(BankDetails).filter(BankDetails.employee_id == employee_id).all()
    work_experience = db.query(EmployeeWorkExperience).filter(EmployeeWorkExperience.employee_id == employee_id).all()
    documents = db.query(EmployeeDocument).filter(EmployeeDocument.employee_id == employee_id).all()
    assets = db.query(Asset).filter(Asset.employee_id == employee_id).all()
    
    department = db.query(Department).filter(Department.department_id == employee.department_id).first() if employee.department_id else None
    shift = db.query(ShiftMaster).filter(ShiftMaster.shift_id == employee.shift_id).first() if employee.shift_id else None
    
    employee_data = {
        "employee_id": employee.employee_id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "department": {
            "department_id": department.department_id,
            "department_name": department.department_name
        } if department else None,
        "designation": employee.designation,
        "joining_date": employee.joining_date,
        "reporting_manager": employee.reporting_manager,
        "email_id": employee.email_id,
        "phone_number": employee.phone_number,
        "location": employee.location,
        "employee_type": employee.employee_type,
        "shift": {
            "shift_id": shift.shift_id,
            "shift_name": shift.shift_name,
            "shift_type": shift.shift_type,
            "start_time": str(shift.start_time),
            "end_time": str(shift.end_time),
            "working_days": shift.working_days
        } if shift else None,
        "profile_photo": employee.profile_photo,
        "created_at": employee.created_at,
        "updated_at": employee.updated_at
    }
    
    return {
        "employee": employee_data,
        "personal_details": personal_details,
        "bank_details": bank_details,
        "work_experience": work_experience,
        "documents": documents,
        "assets": assets
    }

