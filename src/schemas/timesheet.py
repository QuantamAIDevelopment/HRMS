from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class TimesheetBase(BaseModel):
    time_entry_id: Optional[str] = None
    employee_id: Optional[str] = None
    entry_date: Optional[date] = None
    project: Optional[str] = None
    task_description: Optional[str] = None
    hours: Optional[Decimal] = None
    status: Optional[str] = None

class TimesheetCreate(TimesheetBase):
    pass

class TimesheetUpdate(BaseModel):
    time_entry_id: Optional[str] = None
    employee_id: Optional[str] = None
    entry_date: Optional[date] = None
    project: Optional[str] = None
    task_description: Optional[str] = None
    hours: Optional[Decimal] = None
    status: Optional[str] = None

class TimesheetResponse(TimesheetBase):
    approver_id: Optional[str] = None
    approver_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True