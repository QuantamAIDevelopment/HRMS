from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class OffBoardingCreate(BaseModel):
    employee_id: str
    resignation_date: Optional[date] = None
    last_working_day: Optional[date] = None
    reason: Optional[str] = None
    status: Optional[str] = "PENDING"
    full_name: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    it_asset_return: Optional[bool] = False
    access_card_return: Optional[bool] = False
    knowledge_transfer: Optional[bool] = False
    exit_interview: Optional[bool] = False
    final_settlement: Optional[bool] = False
    final_settlement_amount: Optional[float] = None
    checklist_name: Optional[str] = None
    description: Optional[str] = None

class OffBoardingResponse(BaseModel):
    id: int
    employee_id: str
    resignation_date: Optional[date]
    last_working_day: Optional[date]
    reason: Optional[str]
    status: Optional[str] = "PENDING"
    full_name: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    it_asset_return: bool
    access_card_return: bool
    knowledge_transfer: bool
    exit_interview: bool
    final_settlement: bool
    final_settlement_amount: Optional[float] = None
    checklist_name: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    employee_name: Optional[str] = None
    designation: Optional[str] = None
    
    class Config:
        from_attributes = True