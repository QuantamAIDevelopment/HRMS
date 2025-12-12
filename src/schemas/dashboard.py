from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class AttendanceSummary(BaseModel):
    monthly_attendance_percentage: float

class LeaveBalance(BaseModel):
    total_remaining: int
    casual: int
    sick: int
    earned: int

class TimesheetSummary(BaseModel):
    hours_logged_this_week: float

class ExpensesSummary(BaseModel):
    pending_expense_count: int
    total_pending_amount: float

class Birthday(BaseModel):
    name: str
    department: str
    birthday_date: str

class Holiday(BaseModel):
    holiday_name: str
    holiday_date: str

class Document(BaseModel):
    title: str
    category: str

class DashboardResponse(BaseModel):
    attendance: AttendanceSummary
    leave_balance: LeaveBalance
    timesheet: TimesheetSummary
    expenses: ExpensesSummary
    birthdays_this_month: List[Birthday]
    upcoming_holidays: List[Holiday]
    policy_documents: List[Document]