from sqlalchemy import Column, String, Integer, DateTime, Numeric, Text
from sqlalchemy.sql import func
from models.base import Base

class ComponentUpdateLog(Base):
    __tablename__ = "component_update_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False, index=True)
    month = Column(String(20), nullable=False)
    component_name = Column(String(100), nullable=False)
    component_type = Column(String(20), nullable=False)  # "earnings" or "deductions"
    amount = Column(Numeric(12,2), nullable=False)
    action = Column(String(20), nullable=False)  # "added", "updated", "deleted"
    created_at = Column(DateTime, server_default=func.now())