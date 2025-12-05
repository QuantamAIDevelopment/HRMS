from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from src.models.session import get_db
from src.models.Employee_models import Employee
from src.models.employee_personal import EmployeePersonal
from src.models.education import EducationalQualification
from src.models.bank_details import BankDetails
from src.models.assets import Asset
from datetime import datetime
from typing import Optional
from decimal import Decimal
import uuid

router = APIRouter()

@router.post("/onboarding/personal-information")
def create_personal_information(
    employee_id: str = Form(...),
    date_of_birth: str = Form(...),
    gender: str = Form(...),
    marital_status: str = Form(...),
    blood_group: str = Form(...),
    nationality: str = Form(...),
    employee_email: str = Form(...),
    employee_phone: str = Form(...),
    employee_alternate_phone: str = Form(...),
    employee_address: str = Form(...),
    emergency_full_name: str = Form(...),
    emergency_relationship: str = Form(...),
    emergency_primary_phone: str = Form(...),
    emergency_alternate_phone: str = Form(...),
    emergency_address: str = Form(...),
    db: Session = Depends(get_db)
):
    # Convert date string to date object
    dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    
    db_personal = EmployeePersonal(
        id=str(uuid.uuid4()),
        employee_id=employee_id,
        date_of_birth=dob,
        gender=gender,
        marital_status=marital_status,
        blood_group=blood_group,
        nationality=nationality,
        employee_email=employee_email,
        employee_phone=employee_phone,
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
    db.refresh(db_personal)
    return {"message": "Personal information saved successfully"}

@router.post("/onboarding/employment-information")
def create_employment_information(
    employee_id: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email_id: str = Form(...),
    phone_number: str = Form(...),
    full_name: str = Form(None),
    department_id: str = Form(None),
    designation: str = Form(None),
    joining_date: str = Form(None),
    reporting_manager: str = Form(None),
    location: str = Form(None),
    shift_id: str = Form(None),
    profile_photo: str = Form(None),
    status: str = Form("Active"),
    # Work experience fields - optional
    company_name: Optional[str] = Form(None),
    experience_designation: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    from src.models.Employee_models import EmployeeWorkExperience
    
    # Convert string fields to appropriate types with null checks
    dept_id = int(department_id) if department_id else None
    join_date = datetime.strptime(joining_date, "%Y-%m-%d").date() if joining_date else None
    s_id = int(shift_id) if shift_id else None
    
    # Generate full_name if not provided
    if not full_name:
        full_name = f"{first_name} {last_name}"
    
    db_employee = Employee(
        employee_id=employee_id,
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        department_id=dept_id,
        designation=designation,
        joining_date=join_date,
        reporting_manager=reporting_manager,
        email_id=email_id,
        phone_number=phone_number,
        location=location,
        shift_id=s_id,
        profile_photo=profile_photo,
        status=status
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    # Handle work experience - only if fields are provided and not empty
    if (company_name and company_name.strip() and 
        experience_designation and experience_designation.strip()):
        
        # Parse dates if provided
        exp_start_date = None
        exp_end_date = None
        
        if start_date and start_date.strip():
            try:
                exp_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except:
                pass
                
        if end_date and end_date.strip():
            try:
                exp_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            except:
                pass
        
        # Create work experience record
        work_exp = EmployeeWorkExperience(
            employee_id=employee_id,
            company_name=company_name.strip(),
            experience_designation=experience_designation.strip(),
            start_date=exp_start_date,
            end_date=exp_end_date,
            description=description.strip() if description else None
        )
        db.add(work_exp)
        db.commit()
    
    return {"message": "Employment information saved successfully"}

@router.post("/onboarding/educational-qualifications")
def create_educational_qualifications(
    employee_id: str = Form(...),
    course_name: str = Form(...),
    institution_name: str = Form(...),
    specialization: str = Form(...),
    start_year: str = Form(...),
    end_year: str = Form(...),
    grade: str = Form(...),
    skill_name: str = Form(...),
    proficiency_level: str = Form(...),
    db: Session = Depends(get_db)
):
    # Convert string years to integers
    s_year = int(start_year)
    e_year = int(end_year)
    
    db_education = EducationalQualification(
        employee_id=employee_id,
        course_name=course_name,
        institution_name=institution_name,
        specialization=specialization,
        start_year=s_year,
        end_year=e_year,
        grade=grade,
        skill_name=skill_name,
        proficiency_level=proficiency_level
    )
    db.add(db_education)
    db.commit()
    db.refresh(db_education)
    return {"message": "Educational qualifications saved successfully"}

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
    db.refresh(db_bank)
    return {"message": "Bank & tax details saved successfully"}

@router.post("/onboarding/assets-equipment")
def create_assets_equipment(
    serial_number: str = Form(...),
    asset_name: str = Form(...),
    asset_type: str = Form(...),
    assigned_employee_id: str = Form(...),
    status: str = Form(...),
    condition: str = Form(...),
    purchase_date: str = Form(...),
    value: str = Form(...),
    db: Session = Depends(get_db)
):
    # Convert string fields to appropriate types
    p_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
    asset_value = Decimal(value)
    
    db_asset = Asset(
        serial_number=serial_number,
        asset_name=asset_name,
        asset_type=asset_type,
        assigned_employee_id=assigned_employee_id,
        status=status,
        condition=condition,
        purchase_date=p_date,
        value=asset_value
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return {"message": "Assets & equipment assigned successfully"}

@router.post("/onboarding/compensation-details")
def create_compensation_details(
    employee_id: str = Form(...),
    db: Session = Depends(get_db)
):
    # Update existing employee record with compensation details
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db.commit()
    db.refresh(db_employee)
    return {"message": "Compensation details saved successfully"}