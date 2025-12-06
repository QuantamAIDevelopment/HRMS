from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from fastapi import Query
import json



from ...models.session import get_db
from ...models.employee_profile import Employee, EmployeePersonalDetails, BankDetails, EmployeeWorkExperience, EmployeeDocument, ProfileEditRequest, Asset
from ...schemas.profile import ProfileEditRequestCreate

router = APIRouter()

@router.post("/{employee_id}/request-basic-edit")
@router.post("/employees/{employee_id}/request-basic-edit")
def request_basic_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Basic info edit request submitted"}

@router.post("/{employee_id}/request-personal-edit")
@router.post("/employees/{employee_id}/request-personal-edit")
def request_personal_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Personal details edit request submitted"}

@router.post("/{employee_id}/request-bank-edit")
@router.post("/employees/{employee_id}/request-bank-edit")
def request_bank_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Bank details edit request submitted"}

@router.post("/{employee_id}/request-experience-edit")
@router.post("/employees/{employee_id}/request-experience-edit")
def request_experience_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Work experience edit request submitted"}

@router.post("/{employee_id}/request-document-edit")
@router.post("/employees/{employee_id}/request-document-edit")
def request_document_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Document edit request submitted"}

@router.post("/{employee_id}/request-assets-edit")
@router.post("/employees/{employee_id}/request-assets-edit")
def request_assets_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Assets edit request submitted"}

@router.get("/{employee_id}")
@router.get("/employees/{employee_id}")
def get_employee_complete(employee_id: str, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    
    employee = db.query(Employee).options(
        joinedload(Employee.department),
        joinedload(Employee.shift),
        joinedload(Employee.personal_details),
        joinedload(Employee.bank_details),
        joinedload(Employee.work_experience),
        joinedload(Employee.assets)
    ).filter(Employee.employee_id == employee_id).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    documents = db.query(EmployeeDocument).filter(EmployeeDocument.employee_id == employee_id).all()
    assets = db.query(Asset).filter(Asset.assigned_employee_id == employee_id).all()
    
    # Format complete employee data with all relationships
    employee_data = {
        "employee_id": employee.employee_id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "department": {
            "department_id": employee.department.department_id,
            "department_name": employee.department.department_name
        } if employee.department else None,
        "designation": employee.designation,
        "joining_date": employee.joining_date,
        "reporting_manager": employee.reporting_manager,
        "email_id": employee.email_id,
        "phone_number": employee.phone_number,
        "location": employee.location,
        "employee_type": employee.employee_type,
        "shift": {
            "shift_id": employee.shift.shift_id,
            "shift_name": employee.shift.shift_name,
            "shift_type": employee.shift.shift_type,
            "start_time": str(employee.shift.start_time),
            "end_time": str(employee.shift.end_time),
            "working_days": employee.shift.working_days
        } if employee.shift else None,
        "profile_photo": employee.profile_photo,
        "created_at": employee.created_at,
        "updated_at": employee.updated_at
    }
    
    return {
        "employee": employee_data,
        "personal_details": employee.personal_details,
        "bank_details": employee.bank_details,
        "work_experience": employee.work_experience,
        "documents": documents,
        "assets": assets
    }

