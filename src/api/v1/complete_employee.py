from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from core.deps import get_db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from models.Employee_models import (
    Employee, EmployeePersonalDetails, BankDetails, 
    EducationalQualifications, EmployeeDocuments, 
    EmployeeWorkExperience, Assets
)
from models.user import User

from schemas.employee_complete_new import CompleteEmployeeCreateResponse
from core.security import get_password_hash
from services.email_service import send_user_credentials_email
from datetime import datetime, timedelta
from typing import Optional, List, Union
import secrets
import string
import json
import os

router = APIRouter()





@router.get("/all-records")
def get_all_onboarding_records(db: Session = Depends(get_db)):
    from models.Employee_models import Department
    
    # Join Employee with Department to get department names
    employees = db.query(Employee, Department.department_name).outerjoin(
        Department, Employee.department_id == Department.department_id
    ).all()
    
    return {
        "total_records": len(employees),
        "employees": [{
            "employee_id": emp.employee_id,
            "name": f"{emp.first_name} {emp.last_name}",
            "designation": emp.designation,
            "department_id": emp.department_id,
            "department_name": dept_name if dept_name else "No Department",
            "joining_date": str(emp.joining_date),
            "status": emp.status
        } for emp, dept_name in employees]
    }

@router.get("/get-available-assets")
def get_available_assets(db: Session = Depends(get_db)):
    available_assets = db.query(Assets).filter(Assets.status == "Available").all()
    return {
        "total_available": len(available_assets),
        "assets": [{
            "asset_id": asset.asset_id,
            "serial_number": asset.serial_number,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "condition": asset.condition,
            "value": float(asset.value) if asset.value else None
        } for asset in available_assets]
    }

@router.get("/statistics")
def get_onboarding_statistics(db: Session = Depends(get_db)):
    total_employees = db.query(Employee).count()
    active_employees = db.query(Employee).filter(Employee.status == "active").count()
    
    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": total_employees - active_employees
    }

@router.get("/complete-employee/{employee_id}")
def get_complete_employee(employee_id: str, db: Session = Depends(get_db)):
    # Get all employee data
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    personal_details = db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
    bank_details = db.query(BankDetails).filter(BankDetails.employee_id == employee_id).all()
    education = db.query(EducationalQualifications).filter(EducationalQualifications.employee_id == employee_id).all()
    work_experience = db.query(EmployeeWorkExperience).filter(EmployeeWorkExperience.employee_id == employee_id).all()
    documents = db.query(EmployeeDocuments).filter(EmployeeDocuments.employee_id == employee_id).all()
    assets = db.query(Assets).filter(Assets.assigned_employee_id == employee_id).all()
    
    return {
        "employee_info": {
            "employee_id": employee.employee_id,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "email_id": employee.email_id,
            "phone_number": employee.phone_number,
            "department_id": employee.department_id,
            "designation": employee.designation,
            "joining_date": str(employee.joining_date),
            "reporting_manager": employee.reporting_manager,
            "location": employee.location,
            "employment_type": employee.employment_type,
            "annual_ctc": employee.annual_ctc
        },
        "personal_details": {
            "date_of_birth": str(personal_details.date_of_birth) if personal_details else None,
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
        },
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
            "start_date": str(exp.start_date),
            "end_date": str(exp.end_date) if exp.end_date else None,
            "description": exp.description
        } for exp in work_experience],
        "documents": [{
            "document_id": doc.document_id,
            "document_name": doc.document_name,
            "category": doc.category,
            "file_name": doc.file_name,
            "upload_date": str(doc.upload_date),
            "status": doc.status
        } for doc in documents],
        "assets": [{
            "asset_id": asset.asset_id,
            "serial_number": asset.serial_number,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "status": asset.status,
            "condition": asset.condition,
            "purchase_date": str(asset.purchase_date) if asset.purchase_date else None,
            "value": float(asset.value) if asset.value else None
        } for asset in assets]
    }

def generate_temp_password(length=8):
    """Generate a temporary password"""
    characters = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(characters) for _ in range(length))

@router.post("/complete-employee", summary="Create Complete Employee", description="Create a complete employee record with all details including annual CTC")
async def create_complete_employee(
    request: Request,
    # Basic Employee Info
    employee_id: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    
    # Personal Details
    date_of_birth: str = Form(...),
    gender: str = Form(...),
    blood_group: str = Form(...),
    marital_status: str = Form(...),
    nationality: str = Form(...),
    employee_email: str = Form(...),
    employee_phone: str = Form(...),
    employee_alternate_phone: Optional[str] = Form(None),
    employee_address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    pincode: str = Form(...),
    country: str = Form(...),
    
    # Emergency Contact
    emergency_full_name: str = Form(...),
    emergency_relationship: str = Form(...),
    emergency_primary_phone: str = Form(...),
    emergency_alternate_phone: Optional[str] = Form(None),
    emergency_address: str = Form(...),
    
    # Employment Details
    designation: str = Form(...),
    department_name: str = Form(...),
    reporting_manager: Optional[str] = Form(None),
    joining_date: str = Form(...),
    employment_type: str = Form(...),
    location: Optional[str] = Form(None),
    shift_name: Optional[str] = Form("General Shift"),
    start_time: Optional[str] = Form("09:00"),
    end_time: Optional[str] = Form("18:00"),
    annual_ctc: str = Form(..., description="Annual Cost to Company (CTC) in rupees", example="500000"),
    
    # Bank Details
    account_number: str = Form(...),
    account_holder_name: str = Form(...),
    ifsc_code: str = Form(...),
    bank_name: str = Form(...),
    branch: str = Form(...),
    account_type: str = Form(...),
    pan_number: str = Form(...),
    aadhaar_number: str = Form(...),
    
    # Work Experience Fields (Optional - Arrays, can be empty)
    company_name: List[str] = Form([]),
    experience_designation: List[str] = Form([]),
    start_date: List[str] = Form([]),
    end_date: List[str] = Form([]),
    description: List[str] = Form([]),
    
    # Education Fields (Arrays, can be empty)
    course_name: List[str] = Form([]),
    institution_name: List[str] = Form([]),
    specialization: List[str] = Form([]),
    start_year: List[str] = Form([]),  # Changed to string to handle empty values
    end_year: List[str] = Form([]),   # Changed to string to handle empty values
    grade: List[str] = Form([]),
    skill_name: List[str] = Form([]),
    proficiency_level: List[str] = Form([]),
    
    # Document Fields (Arrays with file upload, can be empty)
    document_name: List[str] = Form([]),
    category: List[str] = Form([]),
    files: List[UploadFile] = File(default=[], description="Upload files: images (JPG, PNG), documents (PDF, DOC)"),
    
    # Asset Fields (Single entry only) - Make completely optional
    asset_type: Optional[str] = Form(None),
    serial_number: Optional[str] = Form(None),
    
    # User Creation
    email_id: str = Form(...),
    
    db: Session = Depends(get_db)
):
    try:
        # Log incoming request for debugging
        logger.info(f"Received complete-employee request")
        logger.info(f"Content-Type: {request.headers.get('content-type')}")
        logger.info(f"Employee ID received: {employee_id}")
        # Build work experience list (handle empty values)
        work_exp_list = []
        if company_name:
            for i in range(len(company_name)):
                # Only add if both company_name and designation have actual values
                if (i < len(experience_designation) and 
                    company_name[i] and company_name[i].strip() and 
                    experience_designation[i] and experience_designation[i].strip()):
                    work_exp_list.append({
                        "company_name": company_name[i].strip(),
                        "experience_designation": experience_designation[i].strip(),
                        "start_date": start_date[i].strip() if i < len(start_date) and start_date[i] and start_date[i].strip() else None,
                        "end_date": end_date[i].strip() if i < len(end_date) and end_date[i] and end_date[i].strip() else None,
                        "description": description[i].strip() if i < len(description) and description[i] and description[i].strip() else None
                    })
        
        edu_list = []
        if course_name:
            for i in range(len(course_name)):
                # Only add if both course_name and institution have actual values
                if (i < len(institution_name) and 
                    course_name[i] and course_name[i].strip() and 
                    institution_name[i] and institution_name[i].strip()):
                    edu_list.append({
                        "course_name": course_name[i].strip(),
                        "institution_name": institution_name[i].strip(),
                        "specialization": specialization[i].strip() if i < len(specialization) and specialization[i] and specialization[i].strip() else None,
                        "start_year": int(start_year[i]) if i < len(start_year) and start_year[i] and start_year[i].strip() and start_year[i].isdigit() else None,
                        "end_year": int(end_year[i]) if i < len(end_year) and end_year[i] and end_year[i].strip() and end_year[i].isdigit() else None,
                        "grade": grade[i].strip() if i < len(grade) and grade[i] and grade[i].strip() else None,
                        "skill_name": skill_name[i].strip() if i < len(skill_name) and skill_name[i] and skill_name[i].strip() else None,
                        "proficiency_level": proficiency_level[i].strip() if i < len(proficiency_level) and proficiency_level[i] and proficiency_level[i].strip() else None
                    })
        
        # Handle file uploads and create document list
        doc_list = []
        if document_name:
            for i in range(len(document_name)):
                # Check if document name and category exist
                if (i < len(category) and 
                    document_name[i] and document_name[i].strip() and 
                    category[i] and category[i].strip()):
                    
                    # Check if file exists for this document
                    if (files and i < len(files) and files[i] and 
                        files[i].filename and files[i].filename.strip()):
                        
                        import base64
                        content = await files[i].read()
                        file_base64 = base64.b64encode(content).decode('utf-8')
                        
                        doc_list.append({
                            "document_name": document_name[i].strip(),
                            "category": category[i].strip(),
                            "file_name": files[i].filename,
                            "file_data": file_base64
                        })
                    else:
                        # Add document entry without file (empty value sent)
                        doc_list.append({
                            "document_name": document_name[i].strip(),
                            "category": category[i].strip(),
                            "file_name": "No file uploaded"
                        })
        
        asset_list = []
        # Single Asset Entry
        if asset_type and serial_number:
            asset_list.append({
                "asset_type": asset_type,
                "serial_number": serial_number
            })
        
        # Temporarily disabled duplicate check for testing
        # existing_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        # if existing_employee:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Employee with ID {employee_id} already exists"
        #     )
        
        # Temporarily disabled email duplicate check for testing
        # existing_email = db.query(Employee).filter(Employee.email_id == employee_email).first()
        # if existing_email:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Employee with email {employee_email} already exists"
        #     )
        
        # Temporarily disabled user email duplicate check for testing
        # existing_email_id = db.query(User).filter(User.email == email_id).first()
        # if existing_email_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Email ID {email_id} already exists"
        #     )

        # Find or create department
        from models.Employee_models import ShiftMaster, Department
        department = db.query(Department).filter(Department.department_name == department_name).first()
        if not department:
            department = Department(department_name=department_name)
            db.add(department)
            db.flush()
        
        # Create or find shift
        shift = db.query(ShiftMaster).filter(ShiftMaster.shift_name == shift_name).first()
        if not shift:
            shift = ShiftMaster(
                shift_name=shift_name,
                shift_type="Regular",
                start_time=datetime.strptime(start_time, "%H:%M").time(),
                end_time=datetime.strptime(end_time, "%H:%M").time()
            )
            db.add(shift)
            db.flush()
        
        # 1. Create Employee record
        employee = Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            department_id=department.department_id,
            designation=designation,
            joining_date=datetime.strptime(joining_date, "%Y-%m-%d").date(),
            reporting_manager=reporting_manager or "TBD",
            email_id=email_id,  # Store official email in Employee table
            phone_number=employee_phone,
            location=location or "Office",
            shift_id=shift.shift_id,
            employment_type=employment_type,
            annual_ctc=annual_ctc,
            status="active"
        )
        db.add(employee)
        db.flush()  # Get the employee_id for foreign keys

        # 2. Create Employee Personal Details
        personal_details = EmployeePersonalDetails(
            employee_id=employee_id,
            date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d").date(),
            gender=gender,
            marital_status=marital_status,
            blood_group=blood_group,
            nationality=nationality,
            employee_phone=employee_phone,
            employee_email=employee_email,
            employee_alternate_phone=employee_alternate_phone,
            employee_address=employee_address,
            city=city,
            state=state,
            pincode=pincode,
            country=country,
            emergency_full_name=emergency_full_name,
            emergency_relationship=emergency_relationship,
            emergency_primary_phone=emergency_primary_phone,
            emergency_alternate_phone=emergency_alternate_phone,
            emergency_address=emergency_address
        )
        db.add(personal_details)

        # 3. Create Bank Details
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

        # 4. Create Work Experience records (arrays - only if provided)
        for exp in work_exp_list:
            work_exp = EmployeeWorkExperience(
                employee_id=employee_id,
                experience_designation=exp.get("experience_designation"),
                company_name=exp.get("company_name"),
                start_date=datetime.strptime(exp.get("start_date"), "%Y-%m-%d").date() if exp.get("start_date") else None,
                end_date=datetime.strptime(exp.get("end_date"), "%Y-%m-%d").date() if exp.get("end_date") else None,
                description=exp.get("description")
            )
            db.add(work_exp)

        # 5. Create Education Qualifications
        for edu in edu_list:
            education = EducationalQualifications(
                employee_id=employee_id,
                course_name=edu.get("course_name"),
                institution_name=edu.get("institution_name"),
                specialization=edu.get("specialization"),
                start_year=edu.get("start_year"),
                end_year=edu.get("end_year"),
                grade=edu.get("grade"),
                skill_name=edu.get("skill_name"),
                proficiency_level=edu.get("proficiency_level")
            )
            db.add(education)

        # 6. Create Document records
        for doc in doc_list:
            file_name = doc.get("file_name")
            document = EmployeeDocuments(
                employee_id=employee_id,
                document_name=doc.get("document_name"),
                category=doc.get("category"),
                file_name=file_name,
                file_data=doc.get("file_data"),
                upload_date=datetime.now().date(),
                status="Uploaded" if file_name and file_name != "No file uploaded" else "Pending"
            )
            db.add(document)

        # 7. Assign Assets
        for asset_req in asset_list:
            # Find available asset by serial_number and asset_type
            asset = db.query(Assets).filter(
                Assets.serial_number == asset_req.get("serial_number"),
                Assets.asset_type == asset_req.get("asset_type"),
                Assets.status == "Available"
            ).first()
            
            if asset:
                asset.assigned_employee_id = employee_id
                asset.status = "Assigned"
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Asset with serial number {asset_req.get('serial_number')} and type {asset_req.get('asset_type')} is not available"
                )

        # 8. Generate dummy password and create User
        dummy_password = "TempPass123!"
        hashed_password = get_password_hash(dummy_password)
        
        user = User(
            employee_id=employee_id,
            email=email_id,
            hashed_password=hashed_password,
            full_name=f"{first_name} {last_name}",
            role="EMPLOYEE"
        )
        db.add(user)

        # Commit all changes
        db.commit()

        # 9. Send onboarding email to personal email
        email_sent = False
        try:
            # Create custom email body with official email and temp password
            from services.email_service import send_email
            subject = "Welcome to Company - Your Login Credentials"
            body = f"""Dear {first_name} {last_name},

Welcome to our company! Your official login credentials are:

Official Email: {email_id}
Temporary Password: {dummy_password}

Please login and change your password immediately.

Best regards,
HR Team"""
            
            email_sent = send_email(
                to_email=employee_email,  # Send to personal email
                subject=subject,
                body=body
            )
        except Exception as e:
            print(f"Failed to send onboarding email: {e}")

        # Calculate expiry time (1 day from now)
        expiry_time = datetime.now() + timedelta(days=1)

        # Get all created records for response
        created_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        created_personal = db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
        created_bank = db.query(BankDetails).filter(BankDetails.employee_id == employee_id).all()
        created_education = db.query(EducationalQualifications).filter(EducationalQualifications.employee_id == employee_id).all()
        created_work_exp = db.query(EmployeeWorkExperience).filter(EmployeeWorkExperience.employee_id == employee_id).all()
        created_documents = db.query(EmployeeDocuments).filter(EmployeeDocuments.employee_id == employee_id).all()
        created_assets = db.query(Assets).filter(Assets.assigned_employee_id == employee_id).all()
        
        # Simple response to avoid validation issues
        return {
            "message": "Employee created successfully",
            "employee_id": employee_id,
            "official_email": email_id,
            "temp_password_expires": expiry_time.strftime("%Y-%m-%d %H:%M:%S"),
            "onboarding_email_sent": email_sent,
            "status": "success"
        }

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        print(f"IntegrityError details: {str(e)}")
        if "employee_id" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database says Employee ID {employee_id} already exists. Error: {str(e)}"
            )
        elif "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email address already exists. Error: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database constraint violation: {str(e)}"
            )
    except ValueError as e:
        db.rollback()
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Data validation failed: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Full traceback: {error_traceback}")
        print(f"DETAILED ERROR: {type(e).__name__}: {str(e)}")
        print(f"TRACEBACK: {error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create employee: {type(e).__name__}: {str(e)}"
        )