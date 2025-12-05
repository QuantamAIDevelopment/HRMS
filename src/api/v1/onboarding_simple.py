from fastapi import APIRouter, Form, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from enum import Enum
from src.api.deps import get_db
from src.models.user import User
from src.core.security import get_password_hash
from src.services.email_service import send_otp_email
import random
import string
import json
import os
from src.models.Employee_models import (
    Employee, EmployeePersonalDetails, EducationalQualifications, 
    BankDetails, Assets, EmployeeWorkExperience, ShiftMaster, EmployeeDocuments
)
from src.schemas.Onboarding_schemas import ComprehensiveOnboardingCreate

from datetime import datetime
from decimal import Decimal



router = APIRouter()

def generate_dummy_password(length=8):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits + "@#$"
    return ''.join(random.choice(characters) for _ in range(length))




@router.post("/onboarding/personal-information")
def create_personal_information(
    employee_id: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email_id: str = Form(...),
    phone_number: str = Form(...),
    date_of_birth: str = Form(...),
    gender: str = Form(...),
    blood_group: str = Form(...),
    marital_status: str = Form(...),
    nationality: str = Form(...),
    employee_alternate_phone: str = Form(None),
    employee_address: str = Form(...),
    emergency_full_name: str = Form(...),
    emergency_relationship: str = Form(...),
    emergency_primary_phone: str = Form(...),
    emergency_alternate_phone: str = Form(None),
    emergency_address: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Check if employee already exists
        employee_exists = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        
        if employee_exists:
            raise HTTPException(status_code=400, detail=f"Employee ID {employee_id} already exists. Cannot create new employee.")
        
        # Create employee record
        employee_exists = Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email_id=email_id,
            phone_number=phone_number
        )
        db.add(employee_exists)
        db.flush()
        
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        
        # Create personal details record
        db_personal = EmployeePersonalDetails(
            employee_id=employee_id,
            date_of_birth=dob,
            gender=gender,
            marital_status=marital_status,
            blood_group=blood_group,
            nationality=nationality,
            employee_alternate_phone=employee_alternate_phone,
            employee_address=employee_address,
            emergency_full_name=emergency_full_name,
            emergency_relationship=emergency_relationship,
            emergency_primary_phone=emergency_primary_phone,
            emergency_alternate_phone=emergency_alternate_phone,
            emergency_address=emergency_address
        )
        
        db.add(db_personal)
        db.commit()
        
        # Update employee status
        update_employee_status(employee_id, db)
        
        return {"message": "Personal information saved to employee_personal_details table"}
    except Exception as e:
        db.rollback()
        return {"message": f"Error: {str(e)}"}

@router.post("/onboarding/employment-information")
def create_employment_information(
    employee_id: str = Form(...),
    designation: str = Form(...),
    department_id: int = Form(...),
    reporting_manager: str = Form(...),
    joining_date: str = Form(...),
    employment_type: str = Form(...),
    location: str = Form(...),
    # Experience Fields (supports multiple entries via arrays)
    company_name: List[str] = Form(...),
    experience_designation: List[str] = Form(...),
    start_date: List[str] = Form(...),
    end_date: List[str] = Form(...),
    description: List[str] = Form(...),
    # Shift Fields
    shift_name: str = Form(...),
    shift_type: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        join_date = datetime.strptime(joining_date, "%Y-%m-%d").date()
        
        # Parse time fields for shift
        start_time_obj = datetime.strptime(start_time, "%H:%M").time()
        end_time_obj = datetime.strptime(end_time, "%H:%M").time()
        
        # Create shift master entry - set default working_days since removed from Form
        db_shift = ShiftMaster(
            shift_name=shift_name,
            shift_type=shift_type,
            start_time=start_time_obj,
            end_time=end_time_obj,
            working_days="Monday-Friday"  # Default value
        )
        db.add(db_shift)
        db.flush()  # Get the shift_id
        
        # Check if employee exists, if not return error
        employee_exists = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee_exists:
            return {"message": f"Employee {employee_id} not found. Please create personal information first."}
        
        # Check if reporting manager exists
        if reporting_manager:
            manager_exists = db.query(Employee).filter(Employee.employee_id == reporting_manager).first()
            if not manager_exists:
                return {"message": f"Reporting manager {reporting_manager} not found. Please create the manager first."}
        
        # Update existing employee with employment information
        employee_exists.department_id = department_id
        employee_exists.designation = designation
        employee_exists.joining_date = join_date
        employee_exists.reporting_manager = reporting_manager
        employee_exists.employment_type = employment_type
        employee_exists.location = location
        employee_exists.shift_id = db_shift.shift_id
        # Employee already exists, no need to add
        
        # Add experience information (supports multiple entries)
        for i in range(len(company_name)):
            if (i < len(company_name) and company_name[i] and 
                i < len(experience_designation) and experience_designation[i]):
                    
                    exp_start_date = datetime.strptime(start_date[i], "%Y-%m-%d").date() if i < len(start_date) and start_date[i] else None
                    exp_end_date = datetime.strptime(end_date[i], "%Y-%m-%d").date() if i < len(end_date) and end_date[i] else None
                    resp = description[i] if i < len(description) and description[i] else None
                    
                    db_experience = EmployeeWorkExperience(
                        employee_id=employee_id,
                        company_name=company_name[i],
                        experience_designation=experience_designation[i],
                        start_date=exp_start_date,
                        end_date=exp_end_date,
                        description=resp
                    )
                    db.add(db_experience)
        
        db.commit()
        
        # Update employee status
        update_employee_status(employee_id, db)
        
        return {"message": "Employment information saved to employees table"}
    except Exception as e:
        db.rollback()
        return {"message": f"Error: {str(e)}"}

@router.post("/onboarding/educational-qualifications")
def create_educational_qualifications(
    employee_id: str = Form(...),
    # Education Fields (supports multiple entries via arrays)
    course_name: List[str] = Form(...),
    institution_name: List[str] = Form(...),
    specialization: List[str] = Form([]),
    start_year: List[int] = Form([]),
    end_year: List[int] = Form([]),
    grade: List[str] = Form([]),
    # Skills Fields (supports multiple entries via arrays)
    skill_name: List[str] = Form([]),
    proficiency_level: List[str] = Form([]),
    db: Session = Depends(get_db)
):
    try:
        # Add education qualifications (supports multiple entries)
        for i in range(len(course_name)):
            if (i < len(course_name) and course_name[i] and 
                i < len(institution_name) and institution_name[i]):
                
                spec = specialization[i] if i < len(specialization) and specialization[i] else None
                s_year = start_year[i] if i < len(start_year) and start_year[i] else None
                e_year = end_year[i] if i < len(end_year) and end_year[i] else None
                gr = grade[i] if i < len(grade) and grade[i] else None
                skill = skill_name[i] if i < len(skill_name) and skill_name[i] else None
                prof_level = proficiency_level[i] if i < len(proficiency_level) and proficiency_level[i] else None
                
                db_education = EducationalQualifications(
                    employee_id=employee_id,
                    course_name=course_name[i],
                    institution_name=institution_name[i],
                    specialization=spec,
                    start_year=s_year,
                    end_year=e_year,
                    grade=gr,
                    skill_name=skill,
                    proficiency_level=prof_level
                )
                db.add(db_education)
        
        db.commit()
        
        # Update employee status
        update_employee_status(employee_id, db)
        
        return {"message": "Educational qualifications saved to educational_qualifications table"}
    except Exception as e:
        db.rollback()
        return {"message": f"Error: {str(e)}"}


@router.post("/onboarding/bank-tax-details")
def create_bank_tax_details(
    employee_id: str = Form(...),
    account_number: str = Form(...),
    account_holder_name: str = Form(...),
    ifsc_code: str = Form(...),
    bank_name: str = Form(...),
    branch: str = Form(...),
    account_type: str = Form(...),
    pan_number: str = Form(...),
    aadhaar_number: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        db_bank = BankDetails(
            employee_id=employee_id,
            account_number=account_number,
            account_holder_name=account_holder_name,
            ifsc_code=ifsc_code,
            bank_name=bank_name,
            branch=branch,
            account_type=account_type,
            pan_number=pan_number,
            aadhaar_number=aadhaar_number
        )
        db.add(db_bank)
        db.commit()
        
        # Update employee status
        update_employee_status(employee_id, db)
        
        return {"message": "Bank & tax details saved to bank_details table"}
    except Exception as e:
        db.rollback()
        return {"message": f"Error: {str(e)}"}

@router.get("/onboarding/all-records")
def get_all_onboarding_records(
    db: Session = Depends(get_db)
):
    try:
        employees = db.query(Employee).all()
        return {
            "onboarding_records": [
                {
                    "employee_id": emp.employee_id,
                    "name": f"{emp.first_name} {emp.last_name}",
                    "position": emp.designation,
                    "department": emp.department_id,
                    "joining_date": emp.joining_date.isoformat() if emp.joining_date else None,
                    "annual_ctc": emp.annual_ctc,
                    "status": emp.status
                } for emp in employees
            ]
        }
    except Exception as e:
        return {"message": f"Error: {str(e)}"}

@router.get("/onboarding/get-available-assets")
def get_available_assets(
    db: Session = Depends(get_db)
):
    try:
        # Get available assets with asset_type and serial_number pairs
        available_assets = db.query(Assets.asset_type, Assets.serial_number).filter(Assets.status == "Available").all()
        
        # Group by asset type
        assets_by_type = {}
        for asset_type, serial_number in available_assets:
            if asset_type not in assets_by_type:
                assets_by_type[asset_type] = []
            assets_by_type[asset_type].append(serial_number)
        
        return {
            "available_assets_by_type": assets_by_type
        }
    except Exception as e:
        return {"message": f"Error: {str(e)}"}

@router.post("/onboarding/assign-asset")
def assign_asset(
    assigned_employee_id: str = Form(..., description="Employee ID"),
    asset_type: str = Form(..., description="Asset type from dropdown"),
    serial_number: str = Form(..., description="Serial number from dropdown"),
    db: Session = Depends(get_db)
):
    try:
        existing_asset = db.query(Assets).filter(
            Assets.asset_type == asset_type,
            Assets.serial_number == serial_number,
            Assets.status == "Available"
        ).first()
        
        if existing_asset:
            existing_asset.assigned_employee_id = assigned_employee_id
            existing_asset.status = "Assigned"
            db.commit()
            return {"message": "Asset assigned successfully"}
        else:
            return {"message": "Asset not found or not available"}
    except Exception as e:
        db.rollback()
        return {"message": f"Error: {str(e)}"}

@router.post("/onboarding/compensation-details")
def create_compensation_details(
    employee_id: str = Form(...),
    annual_ctc: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            return {"message": "Employee not found"}
        
        employee.annual_ctc = annual_ctc
        db.commit()
        
        # Update employee status
        update_employee_status(employee_id, db)
        
        return {"message": "Compensation details updated successfully"}
    except Exception as e:
        db.rollback()
        return {"message": f"Error: {str(e)}"}

@router.post("/onboarding/create-user")
def create_user(
    employee_id: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Check if user already exists with this email
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return {"message": "User with this email already exists"}
        
        # Check if employee_id exists in employees table
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            return {"message": "Employee not found with provided ID. Complete onboarding first."}
        
        # Generate dummy password
        dummy_password = generate_dummy_password()
        
        # Create user in users table using employee data
        full_name = f"{employee.first_name} {employee.last_name}" if employee.first_name and employee.last_name else "Employee"
        role = employee.designation if employee.designation else "EMPLOYEE"
        
        new_user = User(
            employee_id=employee_id,
            email=email,
            hashed_password=get_password_hash(dummy_password),
            full_name=full_name,
            role=role
        )
        
        db.add(new_user)
        db.commit()
        
        # Send email with credentials
        email_sent = send_otp_email(email, dummy_password)
        
        return {
            "message": "User created successfully and email sent",
            "employee_id": employee_id,
            "email": email,
            "full_name": full_name,
            "role": role,
            "email_sent": email_sent,
            "status": "Account created and credentials sent via email"
        }
        
    except Exception as e:
        db.rollback()
        return {"message": f"Error: {str(e)}"}


@router.post("/onboarding/complete-with-files")
def create_complete_onboarding_with_files(
    # Required fields
    employee_id: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email_id: str = Form(...),
    phone_number: str = Form(...),
    date_of_birth: str = Form(...),
    gender: str = Form(...),
    blood_group: str = Form(...),
    
    # Optional fields
    marital_status: Optional[str] = Form(None),
    nationality: Optional[str] = Form(None),
    employee_alternate_phone: Optional[str] = Form(None),
    employee_address: Optional[str] = Form(None),
    emergency_full_name: Optional[str] = Form(None),
    emergency_relationship: Optional[str] = Form(None),
    emergency_primary_phone: Optional[str] = Form(None),
    emergency_alternate_phone: Optional[str] = Form(None),
    emergency_address: Optional[str] = Form(None),
    designation: Optional[str] = Form(None),
    department_id: Optional[int] = Form(None),
    reporting_manager: Optional[str] = Form(None),
    joining_date: Optional[str] = Form(None),
    employment_type: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    shift_name: Optional[str] = Form(None),
    shift_type: Optional[str] = Form(None),
    start_time: Optional[str] = Form(None),
    end_time: Optional[str] = Form(None),
    account_number: Optional[str] = Form(None),
    account_holder_name: Optional[str] = Form(None),
    ifsc_code: Optional[str] = Form(None),
    bank_name: Optional[str] = Form(None),
    branch: Optional[str] = Form(None),
    account_type: Optional[str] = Form(None),
    pan_number: Optional[str] = Form(None),
    aadhaar_number: Optional[str] = Form(None),
    annual_ctc: Optional[str] = Form(None),
    
    # JSON arrays
    work_experience: str = Form(default="[]"),
    education_qualifications: str = Form(default="[]"),
    assets: str = Form(default="[]"),
    
    # File uploads
    aadhaar_file: Optional[UploadFile] = File(None),
    pan_file: Optional[UploadFile] = File(None),
    other_documents: Optional[List[UploadFile]] = File(None),
    
    # User creation
    create_user: bool = Form(False),
    user_password: Optional[str] = Form(None),
    
    db: Session = Depends(get_db)
):
    try:
        # Check if employee exists
        employee_exists = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if employee_exists:
            raise HTTPException(status_code=400, detail=f"Employee ID {employee_id} already exists.")
        
        # Check email conflict if creating user
        if create_user:
            existing_user = db.query(User).filter(User.email == email_id).first()
            if existing_user:
                raise HTTPException(status_code=400, detail=f"Email {email_id} already exists")
        
        # Parse JSON arrays
        work_exp_data = json.loads(work_experience) if work_experience != "[]" else []
        education_data = json.loads(education_qualifications) if education_qualifications != "[]" else []
        assets_data = json.loads(assets) if assets != "[]" else []
        
        # Parse dates and times
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        join_date = datetime.strptime(joining_date, "%Y-%m-%d").date() if joining_date else None
        start_time_obj = datetime.strptime(start_time, "%H:%M").time() if start_time else None
        end_time_obj = datetime.strptime(end_time, "%H:%M").time() if end_time else None
        
        # Create shift if provided
        shift_id = None
        if shift_name and shift_type and start_time_obj and end_time_obj:
            db_shift = ShiftMaster(
                shift_name=shift_name,
                shift_type=shift_type,
                start_time=start_time_obj,
                end_time=end_time_obj,
                working_days="Monday-Friday"
            )
            db.add(db_shift)
            db.flush()
            shift_id = db_shift.shift_id
        
        # Create employee
        employee = Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email_id=email_id,
            phone_number=phone_number,
            department_id=department_id,
            designation=designation,
            joining_date=join_date,
            reporting_manager=reporting_manager,
            employment_type=employment_type,
            location=location,
            shift_id=shift_id,
            annual_ctc=annual_ctc
        )
        db.add(employee)
        db.flush()
        
        # Create personal details
        personal_details = EmployeePersonalDetails(
            employee_id=employee_id,
            date_of_birth=dob,
            gender=gender,
            marital_status=marital_status,
            blood_group=blood_group,
            nationality=nationality,
            employee_alternate_phone=employee_alternate_phone,
            employee_address=employee_address,
            emergency_full_name=emergency_full_name,
            emergency_relationship=emergency_relationship,
            emergency_primary_phone=emergency_primary_phone,
            emergency_alternate_phone=emergency_alternate_phone,
            emergency_address=emergency_address
        )
        db.add(personal_details)
        
        # Create bank details if provided
        if account_number:
            bank_details = BankDetails(
                employee_id=employee_id,
                account_number=account_number,
                account_holder_name=account_holder_name,
                ifsc_code=ifsc_code,
                bank_name=bank_name,
                branch=branch,
                account_type=account_type,
                pan_number=pan_number,
                aadhaar_number=aadhaar_number
            )
            db.add(bank_details)
        
        # Add work experience
        for exp in work_exp_data:
            db_experience = EmployeeWorkExperience(
                employee_id=employee_id,
                company_name=exp.get('company_name'),
                experience_designation=exp.get('experience_designation'),
                start_date=datetime.strptime(exp.get('start_date'), "%Y-%m-%d").date() if exp.get('start_date') else None,
                end_date=datetime.strptime(exp.get('end_date'), "%Y-%m-%d").date() if exp.get('end_date') else None,
                description=exp.get('description')
            )
            db.add(db_experience)
        
        # Add education
        for edu in education_data:
            db_education = EducationalQualifications(
                employee_id=employee_id,
                course_name=edu.get('course_name'),
                institution_name=edu.get('institution_name'),
                specialization=edu.get('specialization'),
                start_year=edu.get('start_year'),
                end_year=edu.get('end_year'),
                grade=edu.get('grade'),
                skill_name=edu.get('skill_name'),
                proficiency_level=edu.get('proficiency_level')
            )
            db.add(db_education)
        
        # Handle assets
        for asset in assets_data:
            existing_asset = db.query(Assets).filter(
                Assets.asset_type == asset.get('asset_type'),
                Assets.serial_number == asset.get('serial_number'),
                Assets.status == "Available"
            ).first()
            
            if existing_asset:
                existing_asset.assigned_employee_id = employee_id
                existing_asset.status = "Assigned"
        
        # Handle file uploads
        upload_dir = f"uploads/employees/{employee_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_files = []
        
        # Upload files
        if aadhaar_file:
            aadhaar_path = f"{upload_dir}/aadhaar_{aadhaar_file.filename}"
            with open(aadhaar_path, "wb") as f:
                content = aadhaar_file.file.read()
                f.write(content)
            
            doc = EmployeeDocuments(
                employee_id=employee_id,
                document_name="Aadhaar Card",
                file_name=aadhaar_file.filename,
                file_path=aadhaar_path,
                category="Identity"
            )
            db.add(doc)
            uploaded_files.append("aadhaar")
        
        if pan_file:
            pan_path = f"{upload_dir}/pan_{pan_file.filename}"
            with open(pan_path, "wb") as f:
                content = pan_file.file.read()
                f.write(content)
            
            doc = EmployeeDocuments(
                employee_id=employee_id,
                document_name="PAN Card",
                file_name=pan_file.filename,
                file_path=pan_path,
                category="Identity"
            )
            db.add(doc)
            uploaded_files.append("pan")
        
        if other_documents:
            for i, doc_file in enumerate(other_documents):
                doc_path = f"{upload_dir}/other_{i}_{doc_file.filename}"
                with open(doc_path, "wb") as f:
                    content = doc_file.file.read()
                    f.write(content)
                
                doc = EmployeeDocuments(
                    employee_id=employee_id,
                    document_name=f"Other Document {i+1}",
                    file_name=doc_file.filename,
                    file_path=doc_path,
                    category="Other"
                )
                db.add(doc)
                uploaded_files.append(f"other_{i+1}")
        
        # Create user if requested
        if create_user and user_password:
            user = User(
                employee_id=employee_id,
                email=email_id,
                hashed_password=get_password_hash(user_password),
                full_name=f"{first_name} {last_name}",
                role="EMPLOYEE"
            )
            db.add(user)
        
        db.commit()
        
        update_employee_status(employee_id, db)
        
        return {
            "message": "Complete onboarding saved successfully",
            "employee_id": employee_id,
            "first_name": first_name,
            "last_name": last_name,
            "email_id": email_id,
            "designation": designation,
            "department_id": department_id,
            "user_created": create_user,
            "uploaded_files": uploaded_files,
            "work_experience_count": len(work_exp_data),
            "education_count": len(education_data),
            "assets_count": len(assets_data),
            "status": "Onboarding completed"
        }
        
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        return {"message": f"Error: {str(e)}"}






@router.get("/onboarding/employee/{employee_id}/complete")
def get_employee_complete_details(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Get complete employee details from all tables"""
    try:
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            return {"message": "Employee not found"}
        
        # Get related data
        personal_details = db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
        bank_details = db.query(BankDetails).filter(BankDetails.employee_id == employee_id).all()
        assets = db.query(Assets).filter(Assets.assigned_employee_id == employee_id).all()
        education = db.query(EducationalQualifications).filter(EducationalQualifications.employee_id == employee_id).all()
        work_experience = db.query(EmployeeWorkExperience).filter(EmployeeWorkExperience.employee_id == employee_id).all()
        
        return {
            "employee_info": {
                "employee_id": employee.employee_id,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "email_id": employee.email_id,
                "phone_number": employee.phone_number,
                "department_id": employee.department_id,
                "designation": employee.designation,
                "joining_date": employee.joining_date.isoformat() if employee.joining_date else None,
                "reporting_manager": employee.reporting_manager,
                "location": employee.location,
                "employment_type": employee.employment_type,
                "annual_ctc": employee.annual_ctc
            },
            "personal_details": {
                "date_of_birth": personal_details.date_of_birth.isoformat() if personal_details and personal_details.date_of_birth else None,
                "gender": personal_details.gender if personal_details else None,
                "marital_status": personal_details.marital_status if personal_details else None,
                "blood_group": personal_details.blood_group if personal_details else None,
                "nationality": personal_details.nationality if personal_details else None,
                "employee_alternate_phone": personal_details.employee_alternate_phone if personal_details else None,
                "employee_address": personal_details.employee_address if personal_details else None,
                "emergency_full_name": personal_details.emergency_full_name if personal_details else None,
                "emergency_relationship": personal_details.emergency_relationship if personal_details else None,
                "emergency_primary_phone": personal_details.emergency_primary_phone if personal_details else None,
                "emergency_alternate_phone": personal_details.emergency_alternate_phone if personal_details else None,
                "emergency_address": personal_details.emergency_address if personal_details else None
            } if personal_details else None,
            "bank_details": [{
                "bank_id": bank.bank_id,
                "account_number": bank.account_number,
                "account_holder_name": bank.account_holder_name,
                "ifsc_code": bank.ifsc_code,
                "bank_name": bank.bank_name,
                "branch": bank.branch,
                "account_type": bank.account_type,
                "pan_number": bank.pan_number,
                "aadhaar_number": bank.aadhaar_number
            } for bank in bank_details],
            "assets": [{
                "asset_id": asset.asset_id,
                "serial_number": asset.serial_number,
                "asset_name": asset.asset_name,
                "asset_type": asset.asset_type,
                "status": asset.status,
                "condition": asset.condition,
                "purchase_date": asset.purchase_date.isoformat() if asset.purchase_date else None,
                "value": float(asset.value) if asset.value else 0
            } for asset in assets],
            "education": [{
                "edu_id": edu.edu_id,
                "course_name": edu.course_name,
                "institution_name": edu.institution_name,
                "specialization": edu.specialization,
                "start_year": edu.start_year,
                "end_year": edu.end_year,
                "grade": edu.grade,
                "skill_name": edu.skill_name,
                "proficiency_level": edu.proficiency_level
            } for edu in education],
            "work_experience": [{
                "experience_id": exp.experience_id,
                "experience_designation": exp.experience_designation,
                "company_name": exp.company_name,
                "start_date": exp.start_date.isoformat() if exp.start_date else None,
                "end_date": exp.end_date.isoformat() if exp.end_date else None,
                "description": exp.description
            } for exp in work_experience]
        }
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
@router.get("/onboarding/statistics")
def get_onboarding_statistics(
    db: Session = Depends(get_db)
):
    """Get onboarding statistics - Total, Active, and Completed counts"""
    try:
        # Count total employees
        total_onboarding = db.query(Employee).count()
        
        # Count active (in progress) - employees with status = "inprocess"
        active_count = db.query(Employee).filter(
            Employee.status == "inprocess"
        ).count()
        
        # Count completed - employees with status = "completed"
        completed_count = db.query(Employee).filter(
            Employee.status == "completed"
        ).count()
        
        return {
            "total_onboarding": total_onboarding,
            "active": active_count, 
            "completed": completed_count,
            "statistics": {
                "total_description": "All new hires",
                "active_description": "In progress", 
                "completed_description": "Completed onboarding"
            }
        }
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
def update_employee_status(employee_id: str, db: Session):
    """Automatically update employee status based on onboarding completion"""
    try:
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            return
        
        # Check if all required onboarding steps are completed
        personal_details = db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
        bank_details = db.query(BankDetails).filter(BankDetails.employee_id == employee_id).first()
        documents = db.query(EmployeeDocuments).filter(EmployeeDocuments.employee_id == employee_id).count()
        
        # Check if employee has basic employment info
        has_employment_info = (employee.department_id and employee.designation and 
                              employee.joining_date and employee.shift_id)
        
        # If all required steps are completed, mark as completed
        if (personal_details and bank_details and documents > 0 and 
            has_employment_info and employee.annual_ctc != "0"):
            employee.status = "completed"
        else:
            employee.status = "inprocess"
        
        db.commit()
    except Exception as e:
        db.rollback()