from sqlalchemy import Column, Integer, String, Date, Text
from datetime import datetime
from .base import Base

class Leave(Base):
    __tablename__ = "leave_management"
    
    leave_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, nullable=False)
    leave_type = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String, default="PENDING", nullable=False)
    employee_used_leaves = Column(Integer, default=0)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
