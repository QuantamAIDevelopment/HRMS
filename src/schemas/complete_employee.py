from pydantic import BaseModel, EmailStr
from typing import List
from datetime import date

class CompleteEmployeeRequest(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email_id: EmailStr
    phone_number: str
    date_of_birth: str
    gender: str
    blood_group: str
    marital_status: str
    nationality: str
    employee_alternate_phone: str
    employee_address: str
    emergency_full_name: str
    emergency_relationship: str
    emergency_primary_phone: str
    emergency_alternate_phone: str
    emergency_address: str
    designation: str
    department_id: str
    reporting_manager: str
    joining_date: str
    employment_type: str
    location: str
    shift_name: str
    shift_type: str
    start_time: str
    end_time: str
    account_number: str
    account_holder_name: str
    ifsc_code: str
    bank_name: str
    branch: str
    account_type: str
    pan_number: str
    aadhaar_number: str
    annual_ctc: str
    work_experience: List[str]
    education_qualifications: List[str]
    assets: List[str]

class CompleteEmployeeResponse(BaseModel):
    message: str
    employee_id: str
    uploaded_files: dict