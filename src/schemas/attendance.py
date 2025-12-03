from pydantic import BaseModel
from datetime import date, time
from typing import Optional
from decimal import Decimal

class AttendanceResponse(BaseModel):
    employee_id: str
    employee_name: str
    department: str
    date: date
    punch_in: Optional[time]
    punch_out: Optional[time]
    work_hours: Optional[Decimal]
    status: Optional[str]

    class Config:
        from_attributes = True
