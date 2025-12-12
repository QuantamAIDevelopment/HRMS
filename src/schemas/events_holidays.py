from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class EventsHolidaysCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: str  # Event / Public Holiday / Optional Holiday
    date: date

class EventsHolidaysResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    type: str
    date: date
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True