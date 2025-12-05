from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class SalaryCreate(BaseModel):
    employee_id: str
    designation: str
    pay_cycle: str = "Monthly"
    basic_salary: Optional[Decimal] = None
    hra: Optional[Decimal] = None
    allowance: Optional[Decimal] = None
    provident_fund_percentage: Optional[Decimal] = None
    professional_tax: Optional[Decimal] = None
    month: str
    organization_name: Optional[str] = None

class SalaryResponse(BaseModel):
    payroll_id: int
    employee_id: str
    designation: str
    pay_cycle: str
    basic_salary: Optional[Decimal]
    hra: Optional[Decimal]
    allowance: Optional[Decimal]
    provident_fund_percentage: Optional[Decimal]
    professional_tax: Optional[Decimal]
    total_earnings: Optional[Decimal]
    total_deductions: Optional[Decimal]
    net_salary: Optional[Decimal]
    month: str
    organization_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PayslipResponse(BaseModel):
    payroll_id: int
    employee_id: str
    designation: str
    month: str
    basic_salary: Optional[Decimal]
    hra: Optional[Decimal]
    allowance: Optional[Decimal]
    total_earnings: Optional[Decimal]
    provident_fund_percentage: Optional[Decimal]
    professional_tax: Optional[Decimal]
    total_deductions: Optional[Decimal]
    net_salary: Optional[Decimal]
    pdf_path: Optional[str]
    organization_name: Optional[str]

    class Config:
        from_attributes = True

class PayrollSetupUpdate(BaseModel):
    employee_id: str
    month: str
    basic_salary: Optional[Decimal] = None
    hra: Optional[Decimal] = None
    allowance: Optional[Decimal] = None
    provident_fund_percentage: Optional[Decimal] = None
    professional_tax: Optional[Decimal] = None

class SalaryComponentUpdate(BaseModel):
    employee_id: str
    month: str
    earnings: Optional[List[dict]] = []
    deductions: Optional[List[dict]] = []

class ComponentDelete(BaseModel):
    employee_id: str
    month: str
    component_name: str
    component_type: str  # "earnings" or "deductions"