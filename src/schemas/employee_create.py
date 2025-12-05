from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class WorkExperienceCreate(BaseModel):
    company_name: str
    experience_designation: str
    start_date: date
    end_date: date
    description: Optional[str] = None

class EducationCreate(BaseModel):
    course_name: str
    institution_name: str
    specialization: Optional[str] = None
    start_year: int
    end_year: int
    grade: Optional[str] = None
    skill_name: Optional[str] = None
    proficiency_level: Optional[str] = None

class AssetCreate(BaseModel):
    asset_type: str
    serial_number: str

class EmployeeCreateRequest(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email_id: str
    phone_number: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    marital_status: Optional[str] = None
    nationality: Optional[str] = None
    employee_alternate_phone: Optional[str] = None
    employee_address: Optional[str] = None
    emergency_full_name: Optional[str] = None
    emergency_relationship: Optional[str] = None
    emergency_primary_phone: Optional[str] = None
    emergency_alternate_phone: Optional[str] = None
    emergency_address: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None
    reporting_manager: Optional[str] = None
    joining_date: Optional[date] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    shift_name: Optional[str] = None
    shift_type: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    work_experience: Optional[List[WorkExperienceCreate]] = []
    education_qualifications: Optional[List[EducationCreate]] = []
    assets: Optional[List[AssetCreate]] = []
    account_number: Optional[str] = None
    account_holder_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    bank_name: Optional[str] = None
    branch: Optional[str] = None
    account_type: Optional[str] = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    annual_ctc: Optional[str] = None
    create_user: bool = False
    user_password: Optional[str] = None