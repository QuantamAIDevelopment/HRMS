from sqlalchemy import Column, String, Integer, DateTime, Date, Numeric
from sqlalchemy.sql import func
from src.models.base import Base
from datetime import datetime

class OnboardingProcess(Base):
    __tablename__ = "onboarding_process"

    onboarding_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    position = Column(String(50), nullable=False)
    department = Column(String(50), nullable=False)
    joining_date = Column(Date, nullable=False)
    shifts = Column(String(100))
    status = Column(String(50), default='Pending')
    annual_ctc = Column(Numeric(12,2), default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())