from sqlalchemy import Column, Integer, String, DateTime, Date, Float, Boolean
from datetime import datetime
from src.models.base import Base

class Attendance(Base):
    __tablename__ = "attendance"
    
    attendance_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, nullable=False)
    attendance_date = Column(Date, nullable=False)
    punch_in_time = Column(DateTime, nullable=False)
    punch_out_time = Column(DateTime, nullable=True)
    total_hours = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
