from pydantic import BaseModel

# Manager Summary
class ManagerSummary(BaseModel):
    total_employees_under_manager: int
    pending_leave_requests: int
    growth_percentage: float

# Self-Service Module Response
class ModuleResponse(BaseModel):
    module: str
    description: str
    status: str

# Administrative Tools Response
class TimesheetApprovals(BaseModel):
    pending_timesheets: int
    approved: int
    rejected: int

class LeaveApprovals(BaseModel):
    pending_leaves: int
    approved: int
    rejected: int