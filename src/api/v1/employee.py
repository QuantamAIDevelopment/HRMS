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

@router.post("{employee_id}/request-basic-edit")
def request_basic_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Basic info edit request submitted"}

@router.post("{employee_id}/request-personal-edit")
def request_personal_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Personal details edit request submitted"}

@router.post("{employee_id}/request-bank-edit")
def request_bank_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Bank details edit request submitted"}

@router.post("{employee_id}/request-experience-edit")
def request_experience_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Work experience edit request submitted"}

@router.post("{employee_id}/request-document-edit")
def request_document_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Document edit request submitted"}

@router.post("{employee_id}/request-assets-edit")
def request_assets_edit(employee_id: str, edit_request: ProfileEditRequestCreate, db: Session = Depends(get_db)):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Assets edit request submitted"}

@router.get("/{employee_id}")
def get_employee_complete(employee_id: str, db: Session = Depends(get_db)):
    from sqlalchemy import text
    
    # Get employee basic info
    employee_query = text("""
        SELECT e.employee_id, e.first_name, e.last_name, e.designation, 
               e.joining_date, e.reporting_manager, e.email_id, e.phone_number, 
               e.location, e.employment_type, e.profile_photo, e.created_at, e.updated_at,
               d.department_id, d.department_name,
               s.shift_id, s.shift_name, s.shift_type, s.start_time, s.end_time, s.working_days
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.department_id
        LEFT JOIN shift_master s ON e.shift_id = s.shift_id
        WHERE e.employee_id = :employee_id
    """)
    
    employee_result = db.execute(employee_query, {"employee_id": employee_id}).fetchone()
    
    if not employee_result:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get personal details
    personal_query = text("SELECT * FROM employee_personal_details WHERE employee_id = :employee_id")
    personal_result = db.execute(personal_query, {"employee_id": employee_id}).fetchone()
    
    # Get bank details
    bank_query = text("SELECT * FROM bank_details WHERE employee_id = :employee_id")
    bank_results = db.execute(bank_query, {"employee_id": employee_id}).fetchall()
    
    # Get work experience
    work_query = text("SELECT * FROM employee_work_experience WHERE employee_id = :employee_id")
    work_results = db.execute(work_query, {"employee_id": employee_id}).fetchall()
    
    # Get documents
    doc_query = text("SELECT * FROM employee_documents WHERE employee_id = :employee_id")
    doc_results = db.execute(doc_query, {"employee_id": employee_id}).fetchall()
    
    # Get assets
    asset_query = text("SELECT * FROM assets WHERE employee_id = :employee_id")
    asset_results = db.execute(asset_query, {"employee_id": employee_id}).fetchall()
    
    return {
        "employee": {
            "employee_id": employee_result.employee_id,
            "first_name": employee_result.first_name,
            "last_name": employee_result.last_name,
            "designation": employee_result.designation,
            "joining_date": str(employee_result.joining_date),
            "reporting_manager": employee_result.reporting_manager,
            "email_id": employee_result.email_id,
            "phone_number": employee_result.phone_number,
            "location": employee_result.location,
            "employee_type": employee_result.employment_type,
            "department": {
                "department_id": employee_result.department_id,
                "department_name": employee_result.department_name
            } if employee_result.department_id else None,
            "shift": {
                "shift_id": employee_result.shift_id,
                "shift_name": employee_result.shift_name,
                "shift_type": employee_result.shift_type,
                "start_time": str(employee_result.start_time),
                "end_time": str(employee_result.end_time),
                "working_days": employee_result.working_days
            } if employee_result.shift_id else None
        },
        "personal_details": dict(personal_result._mapping) if personal_result else None,
        "bank_details": [dict(row._mapping) for row in bank_results],
        "work_experience": [dict(row._mapping) for row in work_results],
        "documents": [dict(row._mapping) for row in doc_results],
        "assets": [dict(row._mapping) for row in asset_results]
    }

