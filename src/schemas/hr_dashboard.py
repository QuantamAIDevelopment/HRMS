from pydantic import BaseModel
from typing import Optional
from datetime import date

class EmployeeDetails(BaseModel):
    employee_id: str
    full_name: str
    email_id: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    joining_date: Optional[date] = None

class DashboardSummary(BaseModel):
    employee_details: EmployeeDetails
    total_employees: int
    pending_leave_requests: int
    employee_growth_percent: float

class ModuleResponse(BaseModel):
    title: str
    description: str
    count: Optional[int] = None

class EmployeeResponse(BaseModel):
    id: int
    name: str
    department: str
    position: str