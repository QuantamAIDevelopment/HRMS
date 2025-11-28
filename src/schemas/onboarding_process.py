from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OnboardingProcessBase(BaseModel):
    employee_id: int
    process_name: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    is_mandatory: bool = True

class OnboardingProcessCreate(OnboardingProcessBase):
    pass

class OnboardingProcessResponse(OnboardingProcessBase):
    process_id: int
    status: str
    completed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True