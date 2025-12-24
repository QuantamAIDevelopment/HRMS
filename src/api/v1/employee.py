from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from fastapi import Query
import json

from src.models.session import get_db
from src.core.security import require_employee_role_only
from src.models.Employee_models import EmployeeWorkExperience
from src.models.employee_profile import ProfileEditRequest
from src.models import Employee
from src.models.Employee_models import BankDetails, EmployeeDocuments as EmployeeDocument
from src.models.Employee_models import EmployeePersonalDetailsModel as EmployeePersonalDetails
from src.models.Employee_models import Assets as Asset
from src.schemas.profile import ProfileEditRequestCreate

router = APIRouter()

@router.post("{employee_id}/request-basic-edit")
def request_basic_edit(
    employee_id: str,
    edit_request: ProfileEditRequestCreate,
    current_user: dict = Depends(require_employee_role_only),
    db: Session = Depends(get_db)
):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Basic info edit request submitted"}

@router.post("{employee_id}/request-personal-edit")
def request_personal_edit(
    employee_id: str,
    edit_request: ProfileEditRequestCreate,
    current_user: dict = Depends(require_employee_role_only),
    db: Session = Depends(get_db)
):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Personal details edit request submitted"}

@router.post("{employee_id}/request-bank-edit")
def request_bank_edit(
    employee_id: str,
    edit_request: ProfileEditRequestCreate,
    current_user: dict = Depends(require_employee_role_only),
    db: Session = Depends(get_db)
):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Bank details edit request submitted"}

@router.post("{employee_id}/request-experience-edit")
def request_experience_edit(
    employee_id: str,
    edit_request: ProfileEditRequestCreate,
    current_user: dict = Depends(require_employee_role_only),
    db: Session = Depends(get_db)
):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Work experience edit request submitted"}

@router.post("{employee_id}/request-document-edit")
def request_document_edit(
    employee_id: str,
    edit_request: ProfileEditRequestCreate,
    current_user: dict = Depends(require_employee_role_only),
    db: Session = Depends(get_db)
):
    request = ProfileEditRequest(employee_id=employee_id, **edit_request.dict())
    db.add(request)
    db.commit()
    return {"message": "Document edit request submitted"}

@router.post("{employee_id}/request-assets-edit")
def request_assets_edit(
    employee_id: str,
    edit_request: ProfileEditRequestCreate,
    current_user: dict = Depends(require_employee_role_only),
    db: Session = Depends(get_db)
):
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
        "personal_details": {
            "date_of_birth": str(personal_result.date_of_birth) if personal_result and personal_result.date_of_birth else None,
            "gender": personal_result.gender if personal_result else None,
            "marital_status": personal_result.marital_status if personal_result else None,
            "blood_group": personal_result.blood_group if personal_result else None,
            "nationality": personal_result.nationality if personal_result else None,
            "employee_phone": personal_result.employee_phone if personal_result else None,
            "employee_email": personal_result.employee_email if personal_result else None,
            "employee_alternate_phone": personal_result.employee_alternate_phone if personal_result else None,
            "employee_address": personal_result.employee_address if personal_result else None,
            "city": personal_result.city if personal_result else None,
            "state": personal_result.state if personal_result else None,
            "pincode": personal_result.pincode if personal_result else None,
            "country": personal_result.country if personal_result else None,
            "emergency_full_name": personal_result.emergency_full_name if personal_result else None,
            "emergency_relationship": personal_result.emergency_relationship if personal_result else None,
            "emergency_primary_phone": personal_result.emergency_primary_phone if personal_result else None,
            "emergency_alternate_phone": personal_result.emergency_alternate_phone if personal_result else None,
            "emergency_address": personal_result.emergency_address if personal_result else None
        } if personal_result else None,
        "bank_details": [dict(row._mapping) for row in bank_results],
        "work_experience": [{
            "experience_id": row.experience_id,
            "experience_designation": row.experience_designation,
            "company_name": row.company_name,
            "start_date": str(row.start_date) if row.start_date else None,
            "end_date": str(row.end_date) if row.end_date else None,
            "responsibilities": row.responsibilities
        } for row in work_results],
        "documents": [{
            "document_id": row.document_id,
            "document_name": row.document_name,
            "file_name": row.file_name,
            "category": row.category,
            "upload_date": str(row.upload_date),
            "status": row.status
        } for row in doc_results],
        "assets": [{
            "asset_id": row.asset_id,
            "serial_number": row.serial_number,
            "asset_name": row.asset_name,
            "asset_type": row.asset_type,
            "status": row.status,
            "condition": row.condition,
            "purchase_date": str(row.purchase_date) if row.purchase_date else None,
            "value": float(row.value) if row.value else None
        } for row in asset_results]
    }

