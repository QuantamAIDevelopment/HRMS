from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class EventsHolidaysCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    type: str  # Event / Public Holiday / Optional Holiday
    event_date: date
    location: Optional[str] = 'N/A'

class EventsHolidaysResponse(BaseModel):
    id: int
    title: str
    subtitle: Optional[str]
    type: str
    event_date: date
    location: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True