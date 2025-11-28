from sqlalchemy import Column, String, Integer, DateTime, Numeric, Date
from sqlalchemy.sql import func
from src.models.base import Base
from datetime import datetime

class Payroll(Base):
    __tablename__ = "payroll"
    
    payroll_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=False)
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    basic_salary = Column(Numeric(12, 2), nullable=False)
    allowances = Column(Numeric(12, 2), default=0)
    deductions = Column(Numeric(12, 2), default=0)
    overtime_hours = Column(Numeric(8, 2), default=0)
    overtime_amount = Column(Numeric(12, 2), default=0)
    gross_pay = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(12, 2), default=0)
    net_pay = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), default="PENDING")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)