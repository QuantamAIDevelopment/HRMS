from pydantic import BaseModel
from datetime import date
from typing import Optional

class LeaveCreate(BaseModel):
    employee_id: str
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None

class LeaveResponse(BaseModel):
    leave_id: int
    employee_id: str
    employee_name: Optional[str] = None
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: str

class LeaveApproval(BaseModel):
    leave_id: int
    action: str
    approver_id: str
    comments: Optional[str] = None

class LeaveBalance(BaseModel):
    casual_leave: int = 6
    sick_leave: int = 6
    earned_leaves: int = 6
    total_leaves: int = 18
    employee_used_leaves: int = 0
    used_casual: int = 0
    used_sick: int = 0
    used_earned: int = 0
    remaining_casual: int = 6
    remaining_sick: int = 6
    remaining_earned: int = 6

class ManagerLeaveCreate(BaseModel):
    manager_id: str
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None

class ManagerLeaveResponse(BaseModel):
    leave_id: int
    manager_id: str
    manager_name: Optional[str] = None
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: str
    approved_by: Optional[str] = None
    comments: Optional[str] = None

class ManagerBalanceResponse(BaseModel):
    manager_id: str
    casual_leave: int = 8
    sick_leave: int = 8
    earned_leaves: int = 15
    total_leaves: int = 31
    employee_used_leaves: int = 0
    used_casual: int = 0
    used_sick: int = 0
    used_earned: int = 0
    remaining_casual: int = 8
    remaining_sick: int = 8
    remaining_earned: int = 15

class TeamLeadLeaveCreate(BaseModel):
    team_lead_id: str
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None

class TeamLeadLeaveResponse(BaseModel):
    leave_id: int
    team_lead_id: str
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: str
    approved_by: Optional[str] = None
    comments: Optional[str] = None

class TeamLeadBalanceResponse(BaseModel):
    team_lead_id: str
    casual_leave: int = 7
    sick_leave: int = 10
    earned_leaves: int = 21
    total_leaves: int = 38
    employee_used_leaves: int = 0
    used_casual: int = 0
    used_sick: int = 0
    used_earned: int = 0
    remaining_casual: int = 7
    remaining_sick: int = 10
    remaining_earned: int = 21

class HRExecutiveLeaveCreate(BaseModel):
    hr_executive_id: str
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None

class HRExecutiveLeaveResponse(BaseModel):
    leave_id: int
    hr_executive_id: str
    hr_executive_name: Optional[str] = None
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: str
    approved_by: Optional[str] = None
    comments: Optional[str] = None

class HRExecutiveBalanceResponse(BaseModel):
    hr_executive_id: str
    casual_leave: int = 10
    sick_leave: int = 12
    earned_leaves: int = 25
    total_leaves: int = 47
    employee_used_leaves: int = 0
    used_casual: int = 0
    used_sick: int = 0
    used_earned: int = 0
    remaining_casual: int = 10
    remaining_sick: int = 12
    remaining_earned: int = 25
