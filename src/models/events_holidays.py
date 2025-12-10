from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from .base import Base

class EventsHolidays(Base):
    __tablename__ = "events_holidays"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String(100))
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())