from pydantic import BaseModel
from datetime import date, time
from typing import Optional, List
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

class DailyAttendanceRecord(BaseModel):
    date: date
    day: str
    punch_in: Optional[time]
    punch_out: Optional[time]
    work_hours: Optional[Decimal]
    status: Optional[str]

class AttendanceBreakdown(BaseModel):
    employee_id: str
    employee_name: str
    department: str
    total_work_days: int
    present_days: int
    absent_days: int
    late_days: int
    half_days: int
    leave_days: int
    attendance_rate: float
    total_work_hours: Decimal
    daily_records: List[DailyAttendanceRecord]

    class Config:
        from_attributes = True
