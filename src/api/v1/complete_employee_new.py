from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.core.deps import get_db
from src.models.Employee_models import (
    Employee, EmployeePersonalDetails, BankDetails, 
    EducationalQualifications, EmployeeDocuments, 
    EmployeeWorkExperience, Assets
)
from src.models.user import User
from src.schemas.employee_complete_new import CompleteEmployeeCreateRequest, CompleteEmployeeCreateResponse
from src.core.security import get_password_hash
from src.services.email_service import send_user_credentials_email
from datetime import datetime, timedelta
import secrets
import string

router = APIRouter()

def generate_temp_password(length=8):
    """Generate a temporary password"""
    characters = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(characters) for _ in range(length))

@router.post("/complete-employee-new", response_model=CompleteEmployeeCreateResponse)
async def create_complete_employee_new(
    request: CompleteEmployeeCreateRequest,
    db: Session = Depends(get_db)
):
    try:
        # Check if employee_id already exists
        existing_employee = db.query(Employee).filter(Employee.employee_id == request.employee_id).first()
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with ID {request.employee_id} already exists"
            )
        
        # Check if employee_email already exists
        existing_email = db.query(Employee).filter(Employee.email_id == request.employee_email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with email {request.employee_email} already exists"
            )
        
        # Check if official_email already exists
        existing_official_email = db.query(User).filter(User.email == request.official_email).first()
        if existing_official_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Official email {request.official_email} already exists"
            )

        # 1. Create Employee record
        employee = Employee(
            employee_id=request.employee_id,
            first_name=request.first_name,
            last_name=request.last_name,
            department_id=int(request.department_id),
            designation=request.designation,
            joining_date=datetime.strptime(request.joining_date, "%Y-%m-%d").date(),
            reporting_manager=request.reporting_manager,
            email_id=request.employee_email,
            phone_number=request.employee_phone,
            location=request.location,
            shift_id=1,  # Default shift
            employment_type=request.employment_type,
            status="active"
        )
        db.add(employee)
        db.flush()  # Get the employee_id for foreign keys

        # 2. Create Employee Personal Details
        personal_details = EmployeePersonalDetails(
            employee_id=request.employee_id,
            date_of_birth=datetime.strptime(request.date_of_birth, "%Y-%m-%d").date(),
            gender=request.gender,
            marital_status=request.marital_status,
            blood_group=request.blood_group,
            nationality=request.nationality,
            employee_alternate_phone=request.employee_alternate_phone,
            employee_address=request.employee_address,
            emergency_full_name=request.emergency_full_name,
            emergency_relationship=request.emergency_relationship,
            emergency_primary_phone=request.emergency_primary_phone,
            emergency_alternate_phone=request.emergency_alternate_phone,
            emergency_address=request.emergency_address
        )
        db.add(personal_details)

        # 3. Create Bank Details
        bank_details = BankDetails(
            employee_id=request.employee_id,
            account_number=request.account_number,
            account_holder_name=request.account_holder_name,
            ifsc_code=request.ifsc_code,
            bank_name=request.bank_name,
            branch=request.branch,
            account_type=request.account_type,
            pan_number=request.pan_number,
            aadhaar_number=request.aadhaar_number
        )
        db.add(bank_details)

        # 4. Create Work Experience records (only if provided)
        if request.work_experience:
            for exp in request.work_experience:
                # Only create record if required fields are provided
                if exp.experience_designation and exp.company_name and exp.start_date:
                    work_exp = EmployeeWorkExperience(
                        employee_id=request.employee_id,
                        experience_designation=exp.experience_designation,
                        company_name=exp.company_name,
                        start_date=datetime.strptime(exp.start_date, "%Y-%m-%d").date(),
                        end_date=datetime.strptime(exp.end_date, "%Y-%m-%d").date() if exp.end_date else None,
                        description=exp.description
                    )
                    db.add(work_exp)

        # 5. Create Education Qualifications
        for edu in request.education_qualifications:
            education = EducationalQualifications(
                employee_id=request.employee_id,
                course_name=edu.course_name,
                institution_name=edu.institution_name,
                specialization=edu.specialization,
                start_year=edu.start_year,
                end_year=edu.end_year,
                grade=edu.grade,
                skill_name=edu.skill_name,
                proficiency_level=edu.proficiency_level
            )
            db.add(education)

        # 6. Create Document records
        for doc in request.documents:
            document = EmployeeDocuments(
                employee_id=request.employee_id,
                document_name=doc.document_name,
                category=doc.category,
                file_name=doc.file_name,
                upload_date=datetime.now().date(),
                status="Uploaded"
            )
            db.add(document)

        # 7. Assign Assets
        for asset_req in request.assets:
            # Find available asset by serial_number and asset_type
            asset = db.query(Assets).filter(
                Assets.serial_number == asset_req.serial_number,
                Assets.asset_type == asset_req.asset_type,
                Assets.status == "Available"
            ).first()
            
            if asset:
                asset.assigned_employee_id = request.employee_id
                asset.status = "Assigned"
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Asset with serial number {asset_req.serial_number} and type {asset_req.asset_type} is not available"
                )

        # 8. Generate temporary password and create User
        temp_password = generate_temp_password()
        hashed_password = get_password_hash(temp_password)
        
        user = User(
            employee_id=request.employee_id,
            email=request.official_email,
            hashed_password=hashed_password,
            full_name=f"{request.first_name} {request.last_name}",
            role="EMPLOYEE"
        )
        db.add(user)

        # Update employee with official email
        employee.email_id = request.official_email

        # Commit all changes
        db.commit()

        # 9. Send onboarding email
        email_sent = False
        try:
            email_sent = send_user_credentials_email(
                email=request.employee_email,  # Send to personal email
                password=temp_password
            )
        except Exception as e:
            print(f"Failed to send onboarding email: {e}")

        # Calculate expiry time (1 day from now)
        expiry_time = datetime.now() + timedelta(days=1)

        return CompleteEmployeeCreateResponse(
            message="Employee created successfully with all details",
            employee_id=request.employee_id,
            official_email=request.official_email,
            temp_password_expires=expiry_time.strftime("%Y-%m-%d %H:%M:%S"),
            onboarding_email_sent=email_sent
        )

    except IntegrityError as e:
        db.rollback()
        if "employee_id" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee ID {request.employee_id} already exists"
            )
        elif "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database constraint violation"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create employee: {str(e)}"
        )