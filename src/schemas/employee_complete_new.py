from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

class WorkExperienceCreate(BaseModel):
    experience_designation: Optional[str] = None
    company_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class EducationQualificationCreate(BaseModel):
    course_name: str
    institution_name: str
    start_year: int
    end_year: int
    specialization: Optional[str] = None
    grade: Optional[str] = None
    skill_name: Optional[str] = None
    proficiency_level: Optional[str] = None

class DocumentCreate(BaseModel):
    document_name: str
    category: str
    file_name: str

class AssetAssignCreate(BaseModel):
    asset_type: str
    serial_number: str

class CompleteEmployeeCreateRequest(BaseModel):
    # Basic Employee Info
    employee_id: str
    first_name: str
    last_name: str
    
    # Personal Details
    date_of_birth: str
    gender: str
    blood_group: str
    marital_status: str
    nationality: str
    employee_email: EmailStr
    employee_phone: str
    employee_alternate_phone: Optional[str] = None
    employee_address: str
    
    # Emergency Contact
    emergency_full_name: str
    emergency_relationship: str
    emergency_primary_phone: str
    emergency_alternate_phone: Optional[str] = None
    emergency_address: str
    
    # Employment Details
    designation: str
    department_id: str
    reporting_manager: str
    joining_date: str
    employment_type: str
    location: str
    
    # Bank Details
    account_number: str
    account_holder_name: str
    ifsc_code: str
    bank_name: str
    branch: str
    account_type: str
    pan_number: str
    aadhaar_number: str
    
    # Dynamic Lists
    work_experience: List[WorkExperienceCreate] = []
    education_qualifications: List[EducationQualificationCreate] = []
    documents: List[DocumentCreate] = []
    assets: List[AssetAssignCreate] = []
    
    # User Creation
    official_email: EmailStr

class CompleteEmployeeCreateResponse(BaseModel):
    message: str
    employee_id: str
    official_email: str
    temp_password_expires: str
    onboarding_email_sent: bool