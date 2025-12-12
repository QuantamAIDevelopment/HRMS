from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ProfileBase(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email_id: str
    phone_number: Optional[str] = None
    location: Optional[str] = None
    designation: Optional[str] = None
    joining_date: Optional[date] = None
    department_id: Optional[int] = None
    shift_id: Optional[int] = None
    profile_photo: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_id: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    designation: Optional[str] = None
    joining_date: Optional[date] = None
    department_id: Optional[int] = None
    shift_id: Optional[int] = None
    profile_photo: Optional[str] = None

class ProfileResponse(ProfileBase):
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EmployeeProfileResponse(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    designation: Optional[str] = None
    email_id: str
    phone_number: Optional[str] = None
    location: Optional[str] = None
    profile_photo: Optional[str] = None
    joining_date: Optional[date] = None
    completion_percentage: int
    department: Optional[dict] = None
    shift: Optional[dict] = None
    manager: Optional[dict] = None
    personal_details: Optional[dict] = None
    bank_details: Optional[list] = None

    class Config:
        from_attributes = True

class ProfileSummary(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    designation: Optional[str] = None
    email_id: str
    phone_number: Optional[str] = None
    profile_photo: Optional[str] = None
    completion_percentage: int

class ProfileEditRequestCreate(BaseModel):
    requested_changes: str
    reason: str
    old_value: Optional[str] = None
    new_value: str

class ProfileEditRequestResponse(BaseModel):
    id: int
    employee_id: str
    requested_changes: str
    reason: str
    old_value: Optional[str] = None
    new_value: str
    status: str
    manager_comments: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    document_name: str
    employee_id: str
    file_name: str
    category: str
    upload_date: date
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DepartmentResponse(BaseModel):
    department_id: int
    department_name: str

    class Config:
        from_attributes = True

class ShiftResponse(BaseModel):
    shift_id: int
    shift_name: str
    shift_type: str
    start_time: str
    end_time: str
    working_days: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True