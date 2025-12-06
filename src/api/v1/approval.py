from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from ...models.session import get_db
from ...models.employee_profile import ProfileEditRequest

router = APIRouter()

@router.get("/profile-requests")
@router.get("/approval/profile-requests")
def get_all_profile_requests(db: Session = Depends(get_db)):
    requests = db.query(ProfileEditRequest).all()
    return requests

@router.get("/cards")
@router.get("/approval/cards")
def get_approval_cards(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            COUNT(*) as total_requests,
            COUNT(CASE WHEN UPPER(status) = 'PENDING' THEN 1 END) as pending,
            COUNT(CASE WHEN UPPER(status) = 'APPROVED' THEN 1 END) as approved,
            COUNT(CASE WHEN UPPER(status) = 'REJECTED' THEN 1 END) as rejected
        FROM profile_edit_requests
    """)
    result = db.execute(query).fetchone()
    return {
        "total_requests": result.total_requests or 0,
        "pending": result.pending or 0,
        "approved": result.approved or 0,
        "rejected": result.rejected or 0
    }

@router.put("/employee/{employee_id}")
@router.put("/approval/employee/{employee_id}")
def update_employee_requests(employee_id: str, status: str = Query(...), comments: str = Query(None), db: Session = Depends(get_db)):
    edit_requests = db.query(ProfileEditRequest).filter(
        ProfileEditRequest.employee_id == employee_id,
        ProfileEditRequest.status == "pending"
    ).all()
    
    if not edit_requests:
        return {"message": f"No pending requests found for employee {employee_id}"}
    
    processed_count = 0
    
    for edit_request in edit_requests:
        edit_request.status = status.upper()
        if comments:
            edit_request.manager_comments = comments
        
        if status.upper() == "APPROVED":
            field_name = edit_request.requested_changes.strip().lower()
            new_value = edit_request.new_value
            
            if field_name in ["first_name", "last_name", "email_id", "phone_number", "designation", "location", "reporting_manager", "profile_photo"]:
                query = text(f"UPDATE employees SET {field_name} = :new_value WHERE employee_id = :employee_id")
                db.execute(query, {"new_value": new_value, "employee_id": employee_id})
            elif field_name == "department_id":
                query = text("UPDATE employees SET department_id = :new_value WHERE employee_id = :employee_id")
                db.execute(query, {"new_value": int(new_value), "employee_id": employee_id})
            elif field_name == "shift_id":
                query = text("UPDATE employees SET shift_id = :new_value WHERE employee_id = :employee_id")
                db.execute(query, {"new_value": int(new_value), "employee_id": employee_id})
            elif field_name == "joining_date":
                from datetime import datetime
                query = text("UPDATE employees SET joining_date = :new_value WHERE employee_id = :employee_id")
                db.execute(query, {"new_value": datetime.strptime(new_value, "%Y-%m-%d").date(), "employee_id": employee_id})
            elif field_name in ["experience_designation", "company_name", "start_date", "end_date", "description"]:
                check_query = text("SELECT experience_id FROM employee_work_experience WHERE employee_id = :employee_id ORDER BY created_at DESC LIMIT 1")
                exists = db.execute(check_query, {"employee_id": employee_id}).fetchone()
                if exists:
                    query = text(f"UPDATE employee_work_experience SET {field_name} = :new_value WHERE employee_id = :employee_id")
                    if field_name in ["start_date", "end_date"]:
                        from datetime import datetime
                        db.execute(query, {"new_value": datetime.strptime(new_value, "%Y-%m-%d").date(), "employee_id": employee_id})
                    else:
                        db.execute(query, {"new_value": new_value, "employee_id": employee_id})
                else:
                    if field_name == "experience_designation":
                        query = text("INSERT INTO employee_work_experience (employee_id, experience_designation, company_name, start_date) VALUES (:employee_id, :new_value, 'To be updated', CURRENT_DATE)")
                    elif field_name == "company_name":
                        query = text("INSERT INTO employee_work_experience (employee_id, experience_designation, company_name, start_date) VALUES (:employee_id, 'To be updated', :new_value, CURRENT_DATE)")
                    else:
                        query = text(f"INSERT INTO employee_work_experience (employee_id, experience_designation, company_name, start_date, {field_name}) VALUES (:employee_id, 'To be updated', 'To be updated', CURRENT_DATE, :new_value)")
                    if field_name in ["start_date", "end_date"]:
                        from datetime import datetime
                        db.execute(query, {"new_value": datetime.strptime(new_value, "%Y-%m-%d").date(), "employee_id": employee_id})
                    else:
                        db.execute(query, {"new_value": new_value, "employee_id": employee_id})
            elif field_name in ["serial_number", "asset_name", "asset_type", "condition", "purchase_date", "value"]:
                query = text(f"UPDATE assets SET {field_name} = :new_value WHERE assigned_employee_id = :employee_id")
                if field_name == "purchase_date":
                    from datetime import datetime
                    db.execute(query, {"new_value": datetime.strptime(new_value, "%Y-%m-%d").date(), "employee_id": employee_id})
                elif field_name == "value":
                    db.execute(query, {"new_value": float(new_value), "employee_id": employee_id})
                else:
                    db.execute(query, {"new_value": new_value, "employee_id": employee_id})
            elif field_name in ["date_of_birth", "gender", "marital_status", "blood_group", "nationality", "employee_email", "employee_phone", "employee_alternate_phone", "employee_address", "emergency_full_name", "emergency_relationship", "emergency_primary_phone", "emergency_alternate_phone", "emergency_address"]:
                query = text(f"UPDATE employee_personal_details SET {field_name} = :new_value WHERE employee_id = :employee_id")
                if field_name == "date_of_birth":
                    from datetime import datetime
                    db.execute(query, {"new_value": datetime.strptime(new_value, "%Y-%m-%d").date(), "employee_id": employee_id})
                else:
                    db.execute(query, {"new_value": new_value, "employee_id": employee_id})
            elif field_name in ["account_number", "account_holder_name", "ifsc_code", "bank_name", "branch", "account_type", "pan_number", "aadhaar_number"]:
                query = text(f"UPDATE bank_details SET {field_name} = :new_value WHERE employee_id = :employee_id")
                db.execute(query, {"new_value": new_value, "employee_id": employee_id})
            elif field_name in ["file_name", "category", "upload_date"]:
                query = text(f"UPDATE employee_documents SET {field_name} = :new_value WHERE employee_id = :employee_id")
                if field_name == "upload_date":
                    from datetime import datetime
                    db.execute(query, {"new_value": datetime.strptime(new_value, "%Y-%m-%d").date(), "employee_id": employee_id})
                else:
                    db.execute(query, {"new_value": new_value, "employee_id": employee_id})
        
        processed_count += 1
    
    db.commit()
    return {"message": f"Updated {processed_count} requests to {status.upper()}"}