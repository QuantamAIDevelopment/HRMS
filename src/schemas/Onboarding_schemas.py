from pydantic import BaseModel, EmailStr, validator
from datetime import date
from typing import Optional, List
from decimal import Decimal

# ============================================================
# EMPLOYEE SCHEMAS
# ============================================================

class EmployeeBase(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    department_id: int
    designation: str
    joining_date: date
    reporting_manager: str
    email_id: EmailStr
    phone_number: str
    location: str
    shift_id: int
    employment_type: str
    profile_photo: str

class EmployeeCreate(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    department_id: int
    designation: str
    joining_date: date
    reporting_manager: str
    email_id: EmailStr
    phone_number: str
    location: str
    shift_id: int
    employment_type: str
    profile_photo: str

class EmployeeResponse(EmployeeBase):
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    
    class Config:
        from_attributes = True

# ============================================================
# EMPLOYEE PERSONAL DETAILS SCHEMAS
# ============================================================

class PersonalDetailsBase(BaseModel):
    employee_id: str
    date_of_birth: date
    gender: str
    marital_status: str
    blood_group: str
    nationality: str
    employee_alternate_phone: str
    employee_address: str
    emergency_full_name: str
    emergency_relationship: str
    emergency_primary_phone: str
    emergency_alternate_phone: str
    emergency_address: str

class PersonalDetailsCreate(PersonalDetailsBase):
    pass

class PersonalDetailsResponse(PersonalDetailsBase):
    id: int
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    
    class Config:
        from_attributes = True

# ============================================================
# BANK DETAILS SCHEMAS
# ============================================================

class BankDetailsBase(BaseModel):
    employee_id: str
    account_number: str
    account_holder_name: str
    ifsc_code: str
    bank_name: str
    branch: str
    account_type: str
    pan_number: str
    aadhaar_number: str

class BankDetailsCreate(BankDetailsBase):
    pass

class BankDetailsResponse(BankDetailsBase):
    bank_id: int
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    
    class Config:
        from_attributes = True

# ============================================================
# ASSETS SCHEMAS
# ============================================================

class AssetsBase(BaseModel):
    serial_number: str
    asset_name: str
    asset_type: str
    assigned_employee_id: str
    status: str
    condition: str
    purchase_date: date
    value: Decimal

class AssetsCreate(AssetsBase):
    pass

class AssetsResponse(AssetsBase):
    asset_id: int
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    
    class Config:
        from_attributes = True

# ============================================================
# EDUCATIONAL QUALIFICATIONS SCHEMAS
# ============================================================

class EducationBase(BaseModel):
    employee_id: str
    course_name: str
    institution_name: str
    specialization: str
    start_year: int
    end_year: int
    grade: str
    skill_name: str
    proficiency_level: str

class EducationCreate(EducationBase):
    pass

class EducationResponse(EducationBase):
    edu_id: int
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    
    class Config:
        from_attributes = True

# ============================================================
# EMPLOYEE DOCUMENTS SCHEMAS
# ============================================================

class DocumentsBase(BaseModel):
    employee_id: str
    document_name: str
    file_name: str
    category: str
    upload_date: date
    status: str

class DocumentsCreate(DocumentsBase):
    pass

class DocumentsResponse(DocumentsBase):
    document_id: int
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    
    class Config:
        from_attributes = True

# ============================================================
# SHIFT MASTER SCHEMAS
# ============================================================

class ShiftMasterBase(BaseModel):
    shift_name: str
    shift_type: str
    start_time: str
    end_time: str

class ShiftMasterCreate(ShiftMasterBase):
    pass

class ShiftMasterResponse(ShiftMasterBase):
    shift_id: int
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    
    class Config:
        from_attributes = True


# ============================================================
# COMPREHENSIVE ONBOARDING SCHEMA (ALL FIELDS IN ONE POST)
# ============================================================

class AssetAssignment(BaseModel):
    asset_type: str
    serial_number: str


class WorkExperienceCreate(BaseModel):
    company_name: Optional[str] = None
    experience_designation: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class EducationCreate(BaseModel):
    course_name: str
    institution_name: str
    specialization: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: Optional[str] = None
    skill_name: Optional[str] = None
    proficiency_level: Optional[str] = None


class BankDetailsCreateFull(BaseModel):
    account_number: str
    account_holder_name: str
    ifsc_code: str
    bank_name: str
    branch: str
    account_type: str
    pan_number: str
    aadhaar_number: str


class ComprehensiveOnboardingCreate(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email_id: EmailStr
    phone_number: str
    
    date_of_birth: date
    gender: str
    blood_group: str
    marital_status: str
    nationality: str
    employee_alternate_phone: Optional[str] = None
    employee_address: str
    emergency_full_name: str
    emergency_relationship: str
    emergency_primary_phone: str
    emergency_alternate_phone: Optional[str] = None
    emergency_address: str
    
    designation: str
    department_id: int
    reporting_manager: str
    joining_date: date
    employment_type: str
    location: str
    
    shift_name: str
    shift_type: str
    start_time: str
    end_time: str
    
    work_experience: Optional[List[WorkExperienceCreate]] = []
    
    education_qualifications: Optional[List[EducationCreate]] = None
    
    assets: Optional[List[AssetAssignment]] = None
    
    account_number: str
    account_holder_name: str
    ifsc_code: str
    bank_name: str
    branch: str
    account_type: str
    pan_number: str
    aadhaar_number: str
    
    annual_ctc: str = "0"
    
