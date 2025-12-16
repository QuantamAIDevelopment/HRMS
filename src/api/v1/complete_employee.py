from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from core.deps import get_db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from src.models.Employee_models import (
    Employee, BankDetails, 
    EducationalQualifications, EmployeeDocuments, 
    EmployeeWorkExperience, Assets
)
from src.models.Employee_models import EmployeePersonalDetailsModel as EmployeePersonalDetails
from src.models.user import User

from schemas.employee_complete_new import CompleteEmployeeCreateResponse
from core.security import get_password_hash
from services.email_service import send_user_credentials_email
from datetime import datetime, timedelta
from typing import Optional, List, Union
import secrets
import string
import json
import os

def safe_decode_binary(data):
    """Convert binary data to base64 string"""
    if not data:
        return None
    try:
        import base64
        if isinstance(data, memoryview):
            data = data.tobytes()
        elif isinstance(data, bytes):
            pass  # Already bytes
        else:
            # Convert other types to bytes if possible
            data = bytes(data)
        return base64.b64encode(data).decode('utf-8')
    except Exception as e:
        logger.error(f"Error converting binary data to base64: {e}")
        return None

router = APIRouter()





@router.get("/all-records")
def get_all_onboarding_records(db: Session = Depends(get_db)):
    from src.models.Employee_models import Department
    
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
            "joining_date": str(emp.joining_date)
        } for emp, dept_name in employees]
    }

@router.get("/get-available-assets")
def get_available_assets(db: Session = Depends(get_db)):
    try:
        available_assets = db.query(Assets).filter(Assets.status == "Available").all()
        return {
            "total_available": len(available_assets),
            "assets": [{
                "asset_id": asset.asset_id,
                "serial_number": asset.serial_number,
                "asset_name": asset.asset_name,
                "asset_type": asset.asset_type,
                "condition": asset.condition,
                "value": float(asset.value) if asset.value else 0.0
            } for asset in available_assets]
        }
    except Exception as e:
        return {
            "error": str(e),
            "total_available": 0,
            "assets": []
        }

@router.get("/statistics")
def get_onboarding_statistics(db: Session = Depends(get_db)):
    total_employees = db.query(Employee).count()
    
    return {
        "total_employees": total_employees
    }

@router.get("/managers")
def get_manager_employees(db: Session = Depends(get_db)):
    """Get all employees who are managers (excluding HR managers)"""
    from src.models.Employee_models import Department
    from sqlalchemy import func, or_
    
    # Get all employees who are not in HR department and have designation containing 'Manager' in any case
    managers = db.query(Employee).join(
        Department, Employee.department_id == Department.department_id
    ).filter(
        Department.department_name != "HR",
        or_(
            func.lower(Employee.designation).contains("manager"),
            func.upper(Employee.designation).contains("MANAGER"),
            Employee.designation.ilike("%manager%")
        )
    ).all()
    
    manager_list = []
    for manager in managers:
        manager_list.append({
            "employee_id": manager.employee_id,
            "name": f"{manager.first_name} {manager.last_name}"
        })
    
    return {
        "total_managers": len(manager_list),
        "managers": manager_list
    }



@router.get("/employee-ids")
def get_all_employee_ids(db: Session = Depends(get_db)):
    """Get all employee IDs"""
    employees = db.query(Employee.employee_id).all()
    
    return {
        "total_employees": len(employees),
        "employee_ids": [emp.employee_id for emp in employees]
    }

@router.get("/onboarding-departments")
def get_onboarding_departments(db: Session = Depends(get_db)):
    """Get all departments for onboarding"""
    from src.models.Employee_models import Department
    
    departments = db.query(Department.department_name).all()
    
    return {
        "total_departments": len(departments),
        "departments": [dept.department_name for dept in departments]
    }

@router.get("/test-db")
def test_database_connection(db: Session = Depends(get_db)):
    """Simple test endpoint to check database connectivity"""
    from sqlalchemy import text
    try:
        # Simple query to test database
        count = db.execute(text("SELECT 1")).fetchone()
        return {"status": "Database connection successful", "test_result": count[0]}
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

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
    assets = db.query(Assets).filter(Assets.employee_id == employee_id).all()
    
    # Get department and shift details
    from src.models.Employee_models import Department, ShiftMaster
    department = db.query(Department).filter(Department.department_id == employee.department_id).first() if employee.department_id else None
    shift = db.query(ShiftMaster).filter(ShiftMaster.shift_id == employee.shift_id).first() if employee.shift_id else None
    
    return {
        "employee_info": {
            "employee_id": employee.employee_id,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "email_id": employee.email_id,
            "phone_number": employee.phone_number,
            "department": {
                "department_id": department.department_id,
                "department_name": department.department_name
            } if department else None,
            "designation": employee.designation,
            "joining_date": str(employee.joining_date),
            "reporting_manager": employee.reporting_manager,
            "location": employee.location,
            "shift": {
                "shift_id": shift.shift_id,
                "shift_name": shift.shift_name,
                "shift_type": shift.shift_type,
                "start_time": str(shift.start_time),
                "end_time": str(shift.end_time),
                "working_days": shift.working_days
            } if shift else None,
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
            "description": exp.responsibilities
        } for exp in work_experience],
        "documents": [{
            "document_id": doc.document_id,
            "document_name": doc.document_name,
            "category": doc.category,
            "upload_date": str(doc.upload_date),
            "status": doc.status,
            "file_data": safe_decode_binary(doc.files) if doc.files else None
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

def map_designation_to_role(designation: str) -> str:
    """Map employee designation to appropriate user role"""
    designation_lower = designation.lower()
    
    # Manager roles
    if any(keyword in designation_lower for keyword in ['manager', 'head', 'director', 'lead', 'supervisor']):
        return "MANAGER"
    
    # HR roles
    if any(keyword in designation_lower for keyword in ['hr', 'human resource']):
        if any(keyword in designation_lower for keyword in ['manager', 'head', 'director']):
            return "HR_MANAGER"
        else:
            return "HR_EXECUTIVE"
    
    # Admin roles
    if any(keyword in designation_lower for keyword in ['admin', 'administrator']):
        return "ADMIN"
    
    # Default to employee
    return "EMPLOYEE"

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
        logger.info(f"Personal email (employee_email): {employee_email}")
        logger.info(f"Official email (email_id): {email_id}")
        # Build work experience list (handle empty values)
        work_exp_list = []
        if company_name:
            for i in range(len(company_name)):
                # Only add if both company_name and designation have actual values
                if (i < len(experience_designation) and 
                    company_name[i] and company_name[i].strip() and 
                    experience_designation[i] and experience_designation[i].strip()):
                    
                    # Experience proof files disabled for now
                    proof_file_data = None
                    proof_file_name = None
                    
                    work_exp_list.append({
                        "company_name": company_name[i].strip(),
                        "experience_designation": experience_designation[i].strip(),
                        "start_date": start_date[i].strip() if i < len(start_date) and start_date[i] and start_date[i].strip() else None,
                        "end_date": end_date[i].strip() if i < len(end_date) and end_date[i] and end_date[i].strip() else None,
                        "description": description[i].strip() if i < len(description) and description[i] and description[i].strip() else None,
                        "proof_file_data": proof_file_data,
                        "proof_file_name": proof_file_name
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
        logger.info(f"Processing documents: document_name={document_name}")
        if document_name:
            for i in range(len(document_name)):
                # Check if document name and category exist
                if (i < len(category) and 
                    document_name[i] and document_name[i].strip() and 
                    category[i] and category[i].strip()):
                    
                    # Add document entry without file for now
                    doc_list.append({
                        "document_name": document_name[i].strip(),
                        "category": category[i].strip(),
                        "file_name": "No file uploaded",
                        "files": None
                    })
        logger.info(f"Document list created: {len(doc_list)} documents")
        
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

        # Find manager's employee_id if provided
        manager_employee_id = None
        if reporting_manager and reporting_manager != "TBD":
            manager = db.query(Employee).filter(
                (Employee.first_name + " " + Employee.last_name) == reporting_manager
            ).first()
            if manager:
                manager_employee_id = manager.employee_id
                logger.info(f"Found manager '{reporting_manager}' with ID: {manager_employee_id}")
            else:
                logger.warning(f"Manager '{reporting_manager}' not found, setting to TBD")
                reporting_manager = "TBD"
        
        # Find or create department
        from src.models.Employee_models import ShiftMaster, Department
        department = db.query(Department).filter(Department.department_name == department_name).first()
        if not department:
            department = Department(department_name=department_name)
            db.add(department)
            db.flush()
        
        # Create or find shift using raw SQL to avoid metadata issues
        from sqlalchemy import text
        shift = None
        shift_id = None
        
        try:
            # Try to find existing shift using raw SQL
            result = db.execute(text("""
                SELECT shift_id FROM shift_master 
                WHERE shift_name = :shift_name 
                LIMIT 1
            """), {"shift_name": shift_name})
            
            row = result.fetchone()
            if row:
                shift_id = row[0]
                logger.info(f"Found existing shift with ID: {shift_id}")
            else:
                # Create new shift using raw SQL
                result = db.execute(text("""
                    INSERT INTO shift_master (shift_name, shift_type, start_time, end_time, working_days)
                    VALUES (:shift_name, :shift_type, :start_time, :end_time, :working_days)
                    RETURNING shift_id
                """), {
                    "shift_name": shift_name,
                    "shift_type": "Regular", 
                    "start_time": start_time,
                    "end_time": end_time,
                    "working_days": "Monday-Friday"
                })
                
                row = result.fetchone()
                if row:
                    shift_id = row[0]
                    logger.info(f"Created new shift with ID: {shift_id}")
                    
        except Exception as e:
            logger.error(f"Error with shift operations: {e}")
            # Use default shift_id = 1 if all else fails
            shift_id = 1
        
        # 1. Create Employee record
        employee = Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            department_id=department.department_id,
            designation=designation,
            joining_date=datetime.strptime(joining_date, "%Y-%m-%d").date(),
            reporting_manager=manager_employee_id or "TBD",
            email_id=email_id,  # Store official company email in Employee table
            phone_number=employee_phone,
            location=location or "Office",
            shift_id=shift_id,
            employment_type=employment_type,
            annual_ctc=annual_ctc
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
            employee_email=employee_email,  # Store personal email in personal details
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
        for i, exp in enumerate(work_exp_list):
            work_exp = EmployeeWorkExperience(
                employee_id=employee_id,
                experience_designation=exp.get("experience_designation"),
                company_name=exp.get("company_name"),
                start_date=datetime.strptime(exp.get("start_date"), "%Y-%m-%d").date() if exp.get("start_date") else None,
                end_date=datetime.strptime(exp.get("end_date"), "%Y-%m-%d").date() if exp.get("end_date") else None,
                responsibilities=exp.get("description")
            )
            db.add(work_exp)
            db.flush()  # Get the experience_id
            
            # Experience proof documents disabled for now

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
            file_data = doc.get("files")
            document = EmployeeDocuments(
                employee_id=employee_id,
                document_name=doc.get("document_name"),
                file_name=doc.get("file_name"),
                category=doc.get("category"),
                upload_date=datetime.now().date(),
                status="Uploaded" if file_data else "Pending",
                files=file_data
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
                asset.employee_id = employee_id
                asset.assigned_to = f"{first_name} {last_name}"
                asset.status = "Assigned"
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Asset with serial number {asset_req.get('serial_number')} and type {asset_req.get('asset_type')} is not available"
                )

        # 8. Generate dummy password and create User with designation as role
        dummy_password = "TempPass123!"
        hashed_password = get_password_hash(dummy_password)
        
        user = User(
            employee_id=employee_id,
            email=email_id,
            hashed_password=hashed_password,
            full_name=f"{first_name} {last_name}",
            role=designation
        )
        db.add(user)

        # Update job_titles employee count
        db.execute(
            text("UPDATE job_titles SET employees = (SELECT COUNT(*) FROM employees WHERE designation = job_titles.job_title) WHERE job_title = :designation"),
            {"designation": designation}
        )
        
        # Update shift_master employee count
        db.execute(
            text("UPDATE shift_master SET employees = (SELECT COUNT(*) FROM employees WHERE shift_id = shift_master.shift_id) WHERE shift_id = :shift_id"),
            {"shift_id": shift_id}
        )
        
        # Commit all changes
        db.commit()

        # 9. Send onboarding email to personal email
        email_sent = False
        try:
            email_sent = send_user_credentials_email(
                to_email=employee_email,  # Send to personal email
                employee_id=employee_id,
                password=dummy_password,
                full_name=f"{first_name} {last_name}",
                official_email=email_id  # Official company email for login
            )
            if not email_sent:
                logger.warning(f"Email service not configured - credentials not sent to {employee_email}")
        except Exception as e:
            logger.error(f"Failed to send onboarding email: {e}")
            email_sent = False

        # Calculate expiry time (1 day from now)
        expiry_time = datetime.now() + timedelta(days=1)

        # Get all created records for response
        created_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        created_personal = db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
        created_bank = db.query(BankDetails).filter(BankDetails.employee_id == employee_id).all()
        created_education = db.query(EducationalQualifications).filter(EducationalQualifications.employee_id == employee_id).all()
        created_work_exp = db.query(EmployeeWorkExperience).filter(EmployeeWorkExperience.employee_id == employee_id).all()
        created_documents = db.query(EmployeeDocuments).filter(EmployeeDocuments.employee_id == employee_id).all()
        created_assets = db.query(Assets).filter(Assets.employee_id == employee_id).all()
        
        # Return complete employee information
        return {
            "message": "Employee created successfully",
            "employee_id": employee_id,
            "official_email": email_id,
            "temp_password_expires": expiry_time.strftime("%Y-%m-%d %H:%M:%S"),
            "onboarding_email_sent": email_sent,
            "status": "success",
            "employee_data": {
                "employee_info": {
                    "employee_id": created_employee.employee_id,
                    "first_name": created_employee.first_name,
                    "last_name": created_employee.last_name,
                    "email_id": created_employee.email_id,
                    "phone_number": created_employee.phone_number,
                    "department_id": created_employee.department_id,
                    "designation": created_employee.designation,
                    "joining_date": str(created_employee.joining_date),
                    "reporting_manager": created_employee.reporting_manager,
                    "location": created_employee.location,
                    "employment_type": created_employee.employment_type,
                    "annual_ctc": created_employee.annual_ctc
                },
                "personal_details": {
                    "date_of_birth": str(created_personal.date_of_birth) if created_personal else None,
                    "gender": created_personal.gender if created_personal else None,
                    "marital_status": created_personal.marital_status if created_personal else None,
                    "blood_group": created_personal.blood_group if created_personal else None,
                    "nationality": created_personal.nationality if created_personal else None,
                    "employee_phone": created_personal.employee_phone if created_personal else None,
                    "employee_email": created_personal.employee_email if created_personal else None,
                    "employee_alternate_phone": created_personal.employee_alternate_phone if created_personal else None,
                    "employee_address": created_personal.employee_address if created_personal else None,
                    "city": created_personal.city if created_personal else None,
                    "state": created_personal.state if created_personal else None,
                    "pincode": created_personal.pincode if created_personal else None,
                    "country": created_personal.country if created_personal else None,
                    "emergency_full_name": created_personal.emergency_full_name if created_personal else None,
                    "emergency_relationship": created_personal.emergency_relationship if created_personal else None,
                    "emergency_primary_phone": created_personal.emergency_primary_phone if created_personal else None,
                    "emergency_alternate_phone": created_personal.emergency_alternate_phone if created_personal else None,
                    "emergency_address": created_personal.emergency_address if created_personal else None
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
                } for bank in created_bank],
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
                } for edu in created_education],
                "work_experience": [{
                    "experience_id": exp.experience_id,
                    "experience_designation": exp.experience_designation,
                    "company_name": exp.company_name,
                    "start_date": str(exp.start_date) if exp.start_date else None,
                    "end_date": str(exp.end_date) if exp.end_date else None,
                    "description": exp.responsibilities
                } for exp in created_work_exp],
                "documents": [{
                    "document_id": doc.document_id,
                    "document_name": doc.document_name,
                    "category": doc.category,
                    "upload_date": str(doc.upload_date),
                    "status": doc.status,
                    "file_data": safe_decode_binary(doc.files) if doc.files else None
                } for doc in created_documents],
                "assets": [{
                    "asset_id": asset.asset_id,
                    "serial_number": asset.serial_number,
                    "asset_name": asset.asset_name,
                    "asset_type": asset.asset_type,
                    "status": asset.status,
                    "condition": asset.condition,
                    "purchase_date": str(asset.purchase_date) if asset.purchase_date else None,
                    "value": float(asset.value) if asset.value else None
                } for asset in created_assets]
            }
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