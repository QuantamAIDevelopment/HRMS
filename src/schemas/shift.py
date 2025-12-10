from pydantic import BaseModel
from typing import Optional
from datetime import time, datetime

class ShiftBase(BaseModel):
    shift_name: str
    shift_type: str
    start_time: time
    end_time: time
    working_days: str
    employees: Optional[int] = 0

class ShiftCreate(ShiftBase):
    pass

class ShiftUpdate(BaseModel):
    shift_name: Optional[str] = None
    shift_type: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    working_days: Optional[str] = None
    employees: Optional[int] = None

class ShiftResponse(ShiftBase):
    shift_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True