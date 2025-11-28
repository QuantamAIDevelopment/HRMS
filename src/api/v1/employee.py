from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...models.session import get_db
from ...models.employee_profile import Employee, EmployeePersonalDetails, BankDetails, EmployeeWorkExperience, EmployeeDocument, ProfileEditRequest, Asset
from ...schemas.profile import ProfileEditRequestCreate

router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("/{employee_id}")
def get_employee_complete(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    personal_details = db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
    bank_details = db.query(BankDetails).filter(BankDetails.employee_id == employee_id).all()
    work_experience = db.query(EmployeeWorkExperience).filter(EmployeeWorkExperience.employee_id == employee_id).all()
    documents = db.query(EmployeeDocument).filter(EmployeeDocument.employee_id == employee_id).all()
    assets = db.query(Asset).filter(Asset.assigned_employee_id == employee_id).all()
    
    # Format employee data with department and shift names
    employee_data = {
        "employee_id": employee.employee_id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "department_name": employee.department.department_name if employee.department else None,
        "designation": employee.designation,
        "joining_date": employee.joining_date,
        "reporting_manager": employee.reporting_manager,
        "email_id": employee.email_id,
        "phone_number": employee.phone_number,
        "location": employee.location,
        "shift_name": employee.shift.shift_name if employee.shift else None,
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

@router.post("/{employee_id}/request-basic-edit")
def request_basic_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Basic info edit request submitted"}

@router.post("/{employee_id}/request-personal-edit")
def request_personal_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Personal details edit request submitted"}

@router.post("/{employee_id}/request-bank-edit")
def request_bank_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Bank details edit request submitted"}

@router.post("/{employee_id}/request-experience-edit")
def request_experience_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Work experience edit request submitted"}

@router.post("/{employee_id}/request-document-edit")
def request_document_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Document edit request submitted"}