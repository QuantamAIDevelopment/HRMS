from pydantic import BaseModel, field_validator
from typing import Optional, Union
from datetime import date, datetime
from decimal import Decimal

class TimesheetBase(BaseModel):
    time_entry_id: Optional[str] = None
    employee_id: Optional[str] = None
    entry_date: Optional[Union[date, str]] = None
    project: Optional[str] = None
    task_description: Optional[str] = None
    hours: Optional[Decimal] = None
    status: Optional[str] = None
    
    @field_validator('entry_date')
    @classmethod
    def validate_entry_date(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                # Try multiple date formats
                for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y'):
                    try:
                        return datetime.strptime(v, fmt).date()
                    except ValueError:
                        continue
                raise ValueError('Invalid date format')
            except ValueError:
                raise ValueError('Invalid date format. Use YYYY-MM-DD, DD-MM-YYYY, MM/DD/YYYY, or DD/MM/YYYY')
        return v

class TimesheetCreate(TimesheetBase):
    employee_id: str
    entry_date: Union[date, str]
    project: str
    task_description: str
    hours: Decimal

class TimesheetUpdate(BaseModel):
    time_entry_id: Optional[str] = None
    employee_id: Optional[str] = None
    entry_date: Optional[Union[date, str]] = None
    project: Optional[str] = None
    task_description: Optional[str] = None
    hours: Optional[Decimal] = None
    status: Optional[str] = None
    
    @field_validator('entry_date')
    @classmethod
    def validate_entry_date(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                # Try multiple date formats
                for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y'):
                    try:
                        return datetime.strptime(v, fmt).date()
                    except ValueError:
                        continue
                raise ValueError('Invalid date format')
            except ValueError:
                raise ValueError('Invalid date format. Use YYYY-MM-DD, DD-MM-YYYY, MM/DD/YYYY, or DD/MM/YYYY')
        return v

class TimesheetResponse(TimesheetBase):
    approver_id: Optional[str] = None
    approver_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True