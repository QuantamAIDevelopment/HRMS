from sqlalchemy import Column, String, Integer, DateTime, Numeric, Boolean, Text
from sqlalchemy.sql import func
from src.models.base import Base
from datetime import datetime

class PayrollSetup(Base):
    __tablename__ = "payroll_setup"

    payroll_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    designation = Column(String(100), nullable=False)
    pay_cycle = Column(String(20))
    basic_salary = Column(Numeric(12,2))
    hra = Column(Numeric(12,2))
    allowance = Column(Numeric(12,2))
    bonus_percentage = Column(Numeric(5,2))
    provident_fund_percentage = Column(Numeric(5,2))
    professional_tax = Column(Numeric(12,2))
    total_earnings = Column(Numeric(12,2))
    total_deductions = Column(Numeric(12,2))
    net_salary = Column(Numeric(12,2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    organization_name = Column(String(150))
    pdf_path = Column(Text)
    month = Column(String(20))
    basic_salary_type = Column(String(50))
    hra_type = Column(String(50))
    allowance_type = Column(String(50))
    provident_fund_type = Column(String(50))
    professional_tax_type = Column(String(50))
    component_name = Column(String(100))
    amount = Column(Numeric(12,2))
    component_type = Column(String(50))