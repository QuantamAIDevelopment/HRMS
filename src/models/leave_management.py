from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.sql import func
from .base import Base

class LeaveManagement(Base):
    __tablename__ = "leave_management"

    leave_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="PENDING")  # PENDING, APPROVED, REJECTED
    applied_date = Column(Date, server_default=func.current_date())
    approved_by = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())