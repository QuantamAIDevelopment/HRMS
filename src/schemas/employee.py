from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date
from decimal import Decimal

class DepartmentResponse(BaseModel):
    department_name: str
    
    class Config:
        from_attributes = True

class EmployeeBase(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email_id: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    joining_date: date
    designation: str
    department_id: int
    reporting_manager: Optional[str] = None
    employment_type: Optional[str] = None
    annual_ctc: Optional[Decimal] = None
    profile_photo: Optional[str] = None
    casual_leave: int = 12
    sick_leave: int = 12
    earned_leave: int = 21

class EmployeeListItem(BaseModel):
    employee_id: str
    full_name: str
    email_id: str
    department: str
    designation: str
    reporting_manager: Optional[str] = None
    joining_date: date
    profile_photo: Optional[str] = None
    
    class Config:
        from_attributes = True

class PersonalDetailsResponse(BaseModel):
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_group: Optional[str] = None
    marital_status: Optional[str] = None
    
    class Config:
        from_attributes = True

class BankDetailsResponse(BaseModel):
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    account_holder_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class PayrollSetupResponse(BaseModel):
    basic_salary: Optional[Decimal] = None
    hra: Optional[Decimal] = None
    transport_allowance: Optional[Decimal] = None
    medical_allowance: Optional[Decimal] = None
    pf_contribution: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

class LeaveBalances(BaseModel):
    casual_leave: int
    sick_leave: int
    earned_leave: int

class EmployeeDetailResponse(BaseModel):
    employee_id: str
    full_name: str
    designation: str
    status: str = "Active"  # Default status
    department: str
    email_id: str
    phone_number: Optional[str] = None
    reporting_manager: Optional[str] = None
    joining_date: date
    employment_type: Optional[str] = None
    annual_ctc: Optional[int] = None
    monthly_estimate: Optional[int] = None
    casual_leave: int
    sick_leave: int
    earned_leave: int
    
    class Config:
        from_attributes = True

class EmployeeListResponse(BaseModel):
    total_employees: int
    department_count: int
    new_joiners: int
    employees: List[EmployeeListItem]
    page: int
    size: int

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_id: Optional[str] = None
    status: Optional[str] = None
    department_name: Optional[str] = None
    designation: Optional[str] = None  # role
    reporting_manager: Optional[str] = None
    joining_date: Optional[date] = None
    annual_ctc: Optional[int] = None
    
    @validator('joining_date')
    def validate_joining_date(cls, v):
        if v and v > date.today():
            raise ValueError('Joining date cannot be in the future')
        return v
    
    @validator('department_name')
    def validate_department_name(cls, v):
        if v is not None and v.strip() == '':
            raise ValueError('Department name cannot be empty')
        return v
    
    @validator('annual_ctc')
    def validate_annual_ctc(cls, v):
        if v is not None and v < 0:
            raise ValueError('Annual CTC cannot be negative')
        return v
    
    @validator('reporting_manager')
    def validate_reporting_manager(cls, v):
        if v is not None and v.strip() == '':
            raise ValueError('Reporting manager cannot be empty string')
        return v

class EmployeeUpdateResponse(BaseModel):
    employee_id: str  # Read-only
    full_name: str
    email_id: str
    status: str
    department: str
    designation: str  # role
    reporting_manager: Optional[str] = None
    joining_date: date
    annual_ctc: Optional[int] = None
    # Read-only fields
    casual_leave: int
    sick_leave: int
    earned_leave: int
    
    class Config:
        from_attributes = True