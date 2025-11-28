from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...models.session import get_db
from ...models.employee_profile import ProfileEditRequest, Employee, EmployeePersonalDetails, BankDetails, Asset, EmployeeWorkExperience, EmployeeDocument, Department, ShiftMaster
from ...schemas.profile import ProfileEditRequestResponse

router = APIRouter(prefix="/approvals", tags=["approvals"])

@router.get("/requests")
def get_all_requests(db: Session = Depends(get_db)):
    """Get all profile edit requests"""
    requests = db.query(ProfileEditRequest).all()
    return {
        "total_requests": len(requests),
        "pending_requests": len([r for r in requests if r.status == "pending"]),
        "approved_requests": len([r for r in requests if r.status.upper() == "APPROVED"]),
        "rejected_requests": len([r for r in requests if r.status == "rejected"]),
        "requests": requests
    }

@router.get("/cards")
def get_cards_data(db: Session = Depends(get_db)):
    """Get all card counts in one endpoint"""
    total = db.query(ProfileEditRequest).count()
    pending = db.query(ProfileEditRequest).filter(ProfileEditRequest.status == "pending").count()
    approved = db.query(ProfileEditRequest).filter(ProfileEditRequest.status == "APPROVED").count()
    rejected = db.query(ProfileEditRequest).filter(ProfileEditRequest.status == "rejected").count()
    
    return {
        "total": {"count": total, "title": "Total Requests"},
        "pending": {"count": pending, "title": "Pending Requests"},
        "approved": {"count": approved, "title": "Approved Requests"},
        "rejected": {"count": rejected, "title": "Rejected Requests"}
    }

@router.put("/update-status/{employee_id}")
def update_request_status(employee_id: str, status: str, manager_comments: str = None, db: Session = Depends(get_db)):
    """Update request status by employee ID"""
    
    # Get latest pending request for employee
    request = db.query(ProfileEditRequest).filter(
        ProfileEditRequest.employee_id == employee_id,
        ProfileEditRequest.status == "pending"
    ).order_by(ProfileEditRequest.created_at.desc()).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="No pending request found for employee")
    
    # If approving, apply the changes
    if status.upper() == "APPROVED":
        employee = db.query(Employee).filter(Employee.employee_id == request.employee_id).first()
        
        # Get or create personal details
        personal_details = db.query(EmployeePersonalDetails).filter(
            EmployeePersonalDetails.employee_id == request.employee_id
        ).first()
        if not personal_details:
            personal_details = EmployeePersonalDetails(employee_id=request.employee_id)
            db.add(personal_details)
        
        # Get or create bank details
        bank_details = db.query(BankDetails).filter(
            BankDetails.employee_id == request.employee_id
        ).first()
        if not bank_details:
            bank_details = BankDetails(employee_id=request.employee_id, account_holder_name="Default", ifsc_code="DEFAULT", bank_name="Default Bank")
            db.add(bank_details)
        
        # Apply changes based on requested_changes text
        changes = request.requested_changes.lower()
        
        # Employee table fields
        if "first name" in changes:
            employee.first_name = request.new_value
        if "last name" in changes:
            employee.last_name = request.new_value
        if "designation" in changes or "job title" in changes:
            employee.designation = request.new_value
        if "email" in changes:
            employee.email_id = request.new_value
        if "phone" in changes:
            employee.phone_number = request.new_value
        if "location" in changes:
            employee.location = request.new_value
        if "department" in changes:
            try:
                employee.department_id = int(request.new_value)
            except:
                pass
        if "shift" in changes:
            try:
                employee.shift_id = int(request.new_value)
            except:
                pass
        if "joining" in changes or "hire" in changes:
            employee.joining_date = request.new_value
        if "manager" in changes or "reporting" in changes:
            employee.reporting_manager = request.new_value
        
        # Personal details fields
        if "marital" in changes:
            personal_details.marital_status = request.new_value
        if "gender" in changes:
            personal_details.gender = request.new_value
        if "birth" in changes or "dob" in changes:
            personal_details.date_of_birth = request.new_value
        if "blood" in changes:
            personal_details.blood_group = request.new_value
        if "nationality" in changes:
            personal_details.nationality = request.new_value
        if "address" in changes:
            personal_details.employee_address = request.new_value
        if "emergency" in changes:
            if "name" in changes:
                personal_details.emergency_full_name = request.new_value
            elif "phone" in changes:
                personal_details.emergency_primary_phone = request.new_value
            elif "relationship" in changes:
                personal_details.emergency_relationship = request.new_value
        
        # Bank details fields
        if "account number" in changes:
            bank_details.account_number = request.new_value[:30]
        if "bank name" in changes:
            bank_details.bank_name = request.new_value[:100]
        if "ifsc" in changes:
            bank_details.ifsc_code = request.new_value[:20]
        if "account holder" in changes:
            bank_details.account_holder_name = request.new_value[:50]
        if "branch" in changes:
            bank_details.branch = request.new_value[:150]
        if "account type" in changes:
            bank_details.account_type = request.new_value[:20]
        if "pan" in changes:
            bank_details.pan_number = request.new_value[:15]
        if "aadhaar" in changes:
            bank_details.aadhaar_number = request.new_value[:20]
        
        # Work experience updates
        if "experience" in changes or "company" in changes or "job title" in changes:
            if "job title" in changes:
                # Update existing work experience job title
                work_experiences = db.query(EmployeeWorkExperience).filter(
                    EmployeeWorkExperience.employee_id == request.employee_id
                ).all()
                if work_experiences:
                    work_experiences[0].job_title = request.new_value
                else:
                    # Create new work experience if none exists
                    work_exp = EmployeeWorkExperience(
                        employee_id=request.employee_id,
                        job_title=request.new_value,
                        company_name="Current Company",
                        start_date="2024-01-01"
                    )
                    db.add(work_exp)
            elif "company" in changes:
                work_experiences = db.query(EmployeeWorkExperience).filter(
                    EmployeeWorkExperience.employee_id == request.employee_id
                ).all()
                if work_experiences:
                    work_experiences[0].company_name = request.new_value
        
        # Asset updates
        if "asset" in changes:
            if "assign" in changes:
                # Find asset by name or serial number and assign to employee
                asset = db.query(Asset).filter(
                    (Asset.asset_name == request.new_value) | 
                    (Asset.serial_number == request.new_value)
                ).first()
                if asset:
                    asset.assigned_employee_id = request.employee_id
                    asset.status = "Assigned"
            elif "unassign" in changes or "remove" in changes:
                # Unassign specific asset or all assets from employee
                if request.new_value:
                    asset = db.query(Asset).filter(
                        Asset.assigned_employee_id == request.employee_id,
                        (Asset.asset_name == request.new_value) | 
                        (Asset.serial_number == request.new_value)
                    ).first()
                    if asset:
                        asset.assigned_employee_id = None
                        asset.status = "Available"
                else:
                    # Unassign all assets
                    assets = db.query(Asset).filter(
                        Asset.assigned_employee_id == request.employee_id
                    ).all()
                    for asset in assets:
                        asset.assigned_employee_id = None
                        asset.status = "Available"
            elif "status" in changes:
                # Update asset status
                assets = db.query(Asset).filter(
                    Asset.assigned_employee_id == request.employee_id
                ).all()
                for asset in assets:
                    asset.status = request.new_value
        
        # Document updates - simplified approach
        if "document" in changes:
            if request.old_value:  # Update specific document
                document = db.query(EmployeeDocument).filter(
                    EmployeeDocument.employee_id == request.employee_id,
                    EmployeeDocument.document_name == request.old_value
                ).first()
                if document:
                    document.status = request.new_value
            else:  # Update all documents for employee
                documents = db.query(EmployeeDocument).filter(
                    EmployeeDocument.employee_id == request.employee_id
                ).all()
                for doc in documents:
                    doc.status = request.new_value
    
    # Update request status
    request.status = status.upper()
    if manager_comments:
        request.manager_comments = manager_comments
    
    # Commit all changes
    db.commit()
    
    # Force flush to ensure changes are written to database
    db.flush()
    
    # Refresh all objects to ensure changes are reflected
    if status.upper() == "APPROVED":
        db.refresh(employee)
        if personal_details:
            db.refresh(personal_details)
        if bank_details:
            db.refresh(bank_details)
        
        # Refresh work experience and assets
        work_experiences = db.query(EmployeeWorkExperience).filter(
            EmployeeWorkExperience.employee_id == request.employee_id
        ).all()
        for we in work_experiences:
            db.refresh(we)
        
        assets = db.query(Asset).filter(
            Asset.assigned_employee_id == request.employee_id
        ).all()
        for asset in assets:
            db.refresh(asset)
        
        documents = db.query(EmployeeDocument).filter(
            EmployeeDocument.employee_id == request.employee_id
        ).all()
        for doc in documents:
            db.refresh(doc)
        
        # Final commit to ensure all changes are persisted
        db.commit()
    
    return {"message": f"Request status updated to {status} and profile updated"}