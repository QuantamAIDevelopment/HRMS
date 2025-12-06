from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session, joinedload
from models.session import get_db
from models.Employee_models import Employee
from models.user import User
from core.security import get_password_hash

from typing import Optional, List
import json
import os

router = APIRouter()

@router.get("/employees/{employee_id}")
def get_employee_complete_details(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(Employee).options(
        joinedload(Employee.personal_details),
        joinedload(Employee.bank_details),
        joinedload(Employee.assets),
        joinedload(Employee.education),
        joinedload(Employee.work_experience),
        joinedload(Employee.documents)
    ).filter(Employee.employee_id == employee_id).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {
        "employee_info": {
            "employee_id": employee.employee_id,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "email_id": employee.email_id,
            "phone_number": employee.phone_number,
            "department_id": employee.department_id,
            "designation": employee.designation,
            "joining_date": employee.joining_date,
            "reporting_manager": employee.reporting_manager,
            "location": employee.location,
            "employment_type": employee.employment_type,

            "estimated_gross_salary": float(employee.estimated_gross_salary) if employee.estimated_gross_salary else 0.0,
            "profile_photo": employee.profile_photo
        },
        "personal_details": {
            "date_of_birth": employee.personal_details.date_of_birth if employee.personal_details else None,
            "gender": employee.personal_details.gender if employee.personal_details else None,
            "marital_status": employee.personal_details.marital_status if employee.personal_details else None,
            "blood_group": employee.personal_details.blood_group if employee.personal_details else None,
            "nationality": employee.personal_details.nationality if employee.personal_details else None,
            "employee_email": employee.personal_details.employee_email if employee.personal_details else None,
            "employee_phone": employee.personal_details.employee_phone if employee.personal_details else None,
            "employee_alternate_phone": employee.personal_details.employee_alternate_phone if employee.personal_details else None,
            "employee_address": employee.personal_details.employee_address if employee.personal_details else None,
            "emergency_full_name": employee.personal_details.emergency_full_name if employee.personal_details else None,
            "emergency_relationship": employee.personal_details.emergency_relationship if employee.personal_details else None,
            "emergency_primary_phone": employee.personal_details.emergency_primary_phone if employee.personal_details else None,
            "emergency_alternate_phone": employee.personal_details.emergency_alternate_phone if employee.personal_details else None,
            "emergency_address": employee.personal_details.emergency_address if employee.personal_details else None
        } if employee.personal_details else None,
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
        } for bank in employee.bank_details],
        "assets": [{
            "asset_id": asset.asset_id,
            "serial_number": asset.serial_number,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "status": asset.status,
            "condition": asset.condition,
            "purchase_date": asset.purchase_date,
            "value": asset.value
        } for asset in employee.assets],
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
        } for edu in employee.education],
        "work_experience": [{
            "experience_id": exp.experience_id,
            "experience_designation": exp.experience_designation,
            "company_name": exp.company_name,
            "start_date": exp.start_date,
            "end_date": exp.end_date,
            "description": exp.description
        } for exp in employee.work_experience],
        "documents": [{
            "document_id": doc.document_id,
            "document_name": doc.document_name,
            "file_name": doc.file_name,
            "category": doc.category,
            "upload_date": doc.upload_date,
            "status": doc.status
        } for doc in employee.documents]
    }

@router.get("/employees/{employee_id}/complete")
def get_employee_all_details(employee_id: str, db: Session = Depends(get_db)):
    """Get complete employee details from all tables"""
    employee = db.query(Employee).options(
        joinedload(Employee.personal_details),
        joinedload(Employee.bank_details),
        joinedload(Employee.assets),
        joinedload(Employee.education),
        joinedload(Employee.work_experience),
        joinedload(Employee.documents)
    ).filter(Employee.employee_id == employee_id).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {
        "employee_id": employee.employee_id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email_id": employee.email_id,
        "phone_number": employee.phone_number,
        "department_id": employee.department_id,
        "designation": employee.designation,
        "joining_date": employee.joining_date,
        "reporting_manager": employee.reporting_manager,
        "location": employee.location,
        "employment_type": employee.employment_type,

        "estimated_gross_salary": float(employee.estimated_gross_salary) if employee.estimated_gross_salary else 0.0,
        "personal_details": employee.personal_details.__dict__ if employee.personal_details else None,
        "bank_details": [bank.__dict__ for bank in employee.bank_details],
        "assets": [asset.__dict__ for asset in employee.assets],
        "education": [edu.__dict__ for edu in employee.education],
        "work_experience": [exp.__dict__ for exp in employee.work_experience],
        "documents": [doc.__dict__ for doc in employee.documents]
    }

@router.post("/employees/{employee_id}/{first_name}/{last_name}/{email_id}/{phone_number}")
async def create_employee_with_path_variables(
    employee_id: str,
    first_name: str,
    last_name: str,
    email_id: str,
    phone_number: str,
    
    # Form data
    work_experience: str = Form(default="[]"),
    education_qualifications: str = Form(default="[]"),
    assets: str = Form(default="[]"),
    
    # Bank details
    account_number: Optional[str] = Form(None),
    ifsc_code: Optional[str] = Form(None),
    bank_name: Optional[str] = Form(None),
    
    # Employment details
    designation: Optional[str] = Form(None),
    annual_ctc: Optional[str] = Form(None),
    
    # Document uploads
    aadhaar_file: Optional[UploadFile] = File(None),
    pan_file: Optional[UploadFile] = File(None),
    other_documents: Optional[List[UploadFile]] = File(None),
    
    # User creation
    create_user: bool = Form(False),
    user_password: Optional[str] = Form(None),
    
    db: Session = Depends(get_db)
):
    """Create employee with path variables and document upload"""
    
    # Check if employee exists
    existing = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Employee {employee_id} already exists")
    
    # Check email conflict if creating user
    if create_user:
        existing_user = db.query(User).filter(User.email == email_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail=f"Email {email_id} already exists")
    
    try:
        # Parse JSON data
        work_exp_data = json.loads(work_experience) if work_experience != "[]" else []
        education_data = json.loads(education_qualifications) if education_qualifications != "[]" else []
        assets_data = json.loads(assets) if assets != "[]" else []
        
        # Create employee
        employee = Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email_id=email_id,
            phone_number=phone_number,
            designation=designation,
            estimated_gross_salary=float(annual_ctc) if annual_ctc else None
        )
        db.add(employee)
        db.flush()
        
        # Handle document uploads
        upload_dir = f"uploads/employees/{employee_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Upload documents
        if aadhaar_file:
            aadhaar_path = f"{upload_dir}/aadhaar_{aadhaar_file.filename}"
            with open(aadhaar_path, "wb") as f:
                content = await aadhaar_file.read()
                f.write(content)
        
        if pan_file:
            pan_path = f"{upload_dir}/pan_{pan_file.filename}"
            with open(pan_path, "wb") as f:
                content = await pan_file.read()
                f.write(content)
        
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
        
        return {
            "message": "Employee created successfully",
            "employee_id": employee_id,
            "user_created": create_user,
            "documents_uploaded": {
                "aadhaar": bool(aadhaar_file),
                "pan": bool(pan_file),
                "other_count": len(other_documents) if other_documents else 0
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/employees/create-with-files")
async def create_employee_with_files(
    # Required fields
    employee_id: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email_id: str = Form(...),
    phone_number: str = Form(...),
    date_of_birth: str = Form(...),
    gender: str = Form(...),
    blood_group: str = Form(...),
    
    # Optional personal fields
    marital_status: Optional[str] = Form(None),
    nationality: Optional[str] = Form(None),
    employee_alternate_phone: Optional[str] = Form(None),
    employee_address: Optional[str] = Form(None),
    emergency_full_name: Optional[str] = Form(None),
    emergency_relationship: Optional[str] = Form(None),
    emergency_primary_phone: Optional[str] = Form(None),
    emergency_alternate_phone: Optional[str] = Form(None),
    emergency_address: Optional[str] = Form(None),
    
    # Employment fields
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
    
    # Bank details
    account_number: Optional[str] = Form(None),
    account_holder_name: Optional[str] = Form(None),
    ifsc_code: Optional[str] = Form(None),
    bank_name: Optional[str] = Form(None),
    branch: Optional[str] = Form(None),
    account_type: Optional[str] = Form(None),
    pan_number: Optional[str] = Form(None),
    aadhaar_number: Optional[str] = Form(None),
    annual_ctc: Optional[str] = Form(None),
    
    # Arrays as JSON strings
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
    """Create employee with all form fields and file uploads"""
    
    # Check if employee exists
    existing = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Employee {employee_id} already exists")
    
    # Check email conflict if creating user
    if create_user:
        existing_user = db.query(User).filter(User.email == email_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail=f"Email {email_id} already exists")
    
    try:
        from models.Employee_models import PersonalDetails, BankDetails, Assets, Education, WorkExperience
        
        # Parse JSON arrays
        work_exp_data = json.loads(work_experience) if work_experience != "[]" else []
        education_data = json.loads(education_qualifications) if education_qualifications != "[]" else []
        assets_data = json.loads(assets) if assets != "[]" else []
        
        # Create employee
        employee = Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email_id=email_id,
            phone_number=phone_number,
            designation=designation,
            department_id=department_id,
            reporting_manager=reporting_manager,
            joining_date=joining_date,
            employment_type=employment_type,
            location=location,
            estimated_gross_salary=float(annual_ctc) if annual_ctc else None
        )
        db.add(employee)
        db.flush()
        
        # Add personal details
        personal = PersonalDetails(
            employee_id=employee_id,
            date_of_birth=date_of_birth,
            gender=gender,
            blood_group=blood_group,
            marital_status=marital_status,
            nationality=nationality,
            employee_alternate_phone=employee_alternate_phone,
            employee_address=employee_address,
            emergency_full_name=emergency_full_name,
            emergency_relationship=emergency_relationship,
            emergency_primary_phone=emergency_primary_phone,
            emergency_alternate_phone=emergency_alternate_phone,
            emergency_address=emergency_address
        )
        db.add(personal)
        
        # Add bank details
        if account_number:
            bank = BankDetails(
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
            db.add(bank)
        
        # Add work experience
        for exp in work_exp_data:
            work_exp = WorkExperience(
                employee_id=employee_id,
                company_name=exp.get('company_name'),
                experience_designation=exp.get('experience_designation'),
                start_date=exp.get('start_date'),
                end_date=exp.get('end_date'),
                description=exp.get('description')
            )
            db.add(work_exp)
        
        # Add education
        for edu in education_data:
            education = Education(
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
            db.add(education)
        
        # Add assets
        for asset in assets_data:
            asset_record = Assets(
                employee_id=employee_id,
                asset_type=asset.get('asset_type'),
                serial_number=asset.get('serial_number')
            )
            db.add(asset_record)
        
        # Handle file uploads
        upload_dir = f"uploads/employees/{employee_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_files = []
        
        # Upload files
        if aadhaar_file:
            aadhaar_path = f"{upload_dir}/aadhaar_{aadhaar_file.filename}"
            with open(aadhaar_path, "wb") as f:
                content = await aadhaar_file.read()
                f.write(content)
            uploaded_files.append("aadhaar")
        
        if pan_file:
            pan_path = f"{upload_dir}/pan_{pan_file.filename}"
            with open(pan_path, "wb") as f:
                content = await pan_file.read()
                f.write(content)
            uploaded_files.append("pan")
        
        if other_documents:
            for i, doc_file in enumerate(other_documents):
                doc_path = f"{upload_dir}/other_{i}_{doc_file.filename}"
                with open(doc_path, "wb") as f:
                    content = await doc_file.read()
                    f.write(content)
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
        
        return {
            "message": "Employee created successfully",
            "employee_id": employee_id,
            "user_created": create_user,
            "work_experience_count": len(work_exp_data),
            "education_count": len(education_data),
            "assets_count": len(assets_data),
            "uploaded_files": uploaded_files
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/employees/upload-documents/{employee_id}")
async def upload_employee_documents(
    employee_id: str,
    aadhaar_file: Optional[UploadFile] = File(None),
    pan_file: Optional[UploadFile] = File(None),
    other_documents: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """Upload documents for existing employee"""
    
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    try:
        from models.Employee_models import Documents
        
        # Create upload directory
        upload_dir = f"uploads/employees/{employee_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_files = []
        
        # Upload Aadhaar
        if aadhaar_file:
            aadhaar_path = f"{upload_dir}/aadhaar_{aadhaar_file.filename}"
            with open(aadhaar_path, "wb") as f:
                content = await aadhaar_file.read()
                f.write(content)
            
            doc = Documents(
                employee_id=employee_id,
                document_name="Aadhaar Card",
                file_name=aadhaar_file.filename,
                file_path=aadhaar_path,
                category="Identity"
            )
            db.add(doc)
            uploaded_files.append("aadhaar")
        
        # Upload PAN
        if pan_file:
            pan_path = f"{upload_dir}/pan_{pan_file.filename}"
            with open(pan_path, "wb") as f:
                content = await pan_file.read()
                f.write(content)
            
            doc = Documents(
                employee_id=employee_id,
                document_name="PAN Card",
                file_name=pan_file.filename,
                file_path=pan_path,
                category="Identity"
            )
            db.add(doc)
            uploaded_files.append("pan")
        
        # Upload other documents
        if other_documents:
            for i, doc_file in enumerate(other_documents):
                doc_path = f"{upload_dir}/other_{i}_{doc_file.filename}"
                with open(doc_path, "wb") as f:
                    content = await doc_file.read()
                    f.write(content)
                
                doc = Documents(
                    employee_id=employee_id,
                    document_name=f"Other Document {i+1}",
                    file_name=doc_file.filename,
                    file_path=doc_path,
                    category="Other"
                )
                db.add(doc)
                uploaded_files.append(f"other_{i+1}")
        
        db.commit()
        
        return {
            "message": "Documents uploaded successfully",
            "employee_id": employee_id,
            "uploaded_files": uploaded_files
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading documents: {str(e)}")