from .base import Base
from .user import User
from .job_title import JobTitle
from .timesheet import Timesheet
from .shift import Shift
from .off_boarding import OffBoarding
from .events_holidays import EventsHolidays
from .policy import Policy
from .leave import Leave
from .hrms_models import (
    Attendance, Expense, TimeEntry, 
    LeaveManagement, ComplianceDocument
)
from .Employee_models import (
    Employee, Department, ShiftMaster, Assets, EmployeePersonalDetailsModel as EmployeePersonalDetails, 
    BankDetails, EducationalQualifications, 
    EmployeeDocuments, EmployeeWorkExperience
)
# Remove conflicting employee.py import - use Employee_models.py only

# Create alias for backward compatibility
EmployeePersonal = EmployeePersonalDetails

__all__ = [
    "Base",
    "User",
    "Employee",
    "Department", 
    "Policy",
    "ComplianceDocument",
    "EmployeePersonal",
    "Attendance",
    "Expense",
    "TimeEntry",
    "ShiftMaster",
    "LeaveManagement",
    "Leave",
    "Assets",
    "EmployeeDocuments",
    "EmployeePersonalDetails",
    "BankDetails",
    "JobTitle",
    "Timesheet",
    "Shift",
    "OffBoarding",
    "EventsHolidays"
]