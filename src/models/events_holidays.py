from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from .base import Base

class EventsHolidays(Base):
    __tablename__ = "events_holidays"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    subtitle = Column(String(200))
    type = Column(String(50), nullable=False)  # Event / Public Holiday / Optional Holiday
    event_date = Column(Date, nullable=False)
    location = Column(String(100), default='N/A')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())