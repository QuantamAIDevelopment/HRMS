from sqlalchemy import Column, String, Integer, DateTime, Numeric, Text, CheckConstraint, ForeignKey, Index, JSON
from sqlalchemy.sql import func
from .base import Base

class PayrollSetup(Base):
    __tablename__ = "payroll_setup"

    payroll_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False, index=True)
    designation = Column(String(100), nullable=False)
    pay_cycle = Column(String(20), default="Monthly")

    basic_salary = Column(Numeric(12,2))
    hra = Column(Numeric(12,2))
    allowance = Column(Numeric(12,2))
  
    provident_fund_percentage = Column(Numeric(5,2))
    professional_tax = Column(Numeric(12,2))
    total_earnings = Column(Numeric(12,2))
    total_deductions = Column(Numeric(12,2))
    net_salary = Column(Numeric(12,2))
    
    pdf_path = Column(String(255))
    
    month = Column(String(20), index=True)
    basic_salary_type = Column(String(50))
    hra_type = Column(String(50))
    allowance_type = Column(String(50))
    provident_fund_type = Column(String(50))
    professional_tax_type = Column(String(50))
    
    salary_components = Column(JSON, default='{}')
    
    organization_name = Column(String(100))
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_payroll_employee_id', 'employee_id'),
        Index('idx_payroll_month', 'month'),
        Index('idx_employee_month', 'employee_id', 'month'),
        CheckConstraint('length(employee_id) > 0', name='check_employee_id_not_empty'),
        {'extend_existing': True}
    )