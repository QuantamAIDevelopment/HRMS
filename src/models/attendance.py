from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .base import Base

class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = {'extend_existing': True}
    
    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), nullable=False)
    attendance_date = Column(Date, nullable=False)
    punch_in = Column(Time)
    punch_out = Column(Time)
    work_hours = Column(Numeric(5, 2))
    status = Column(String(50))
    policy_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
