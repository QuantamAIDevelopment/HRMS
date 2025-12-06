from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from models.base import Base

class OnboardingProcess(Base):
    __tablename__ = "onboarding_process"

    process_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False, index=True)
    step_name = Column(String(100), nullable=False)
    status = Column(String(20), default="pending")
    completed_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())