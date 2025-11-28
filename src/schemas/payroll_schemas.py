from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

class PayrollBase(BaseModel):
    employee_id: int
    pay_period_start: date
    pay_period_end: date
    basic_salary: Decimal
    allowances: Decimal = 0
    deductions: Decimal = 0
    overtime_hours: Decimal = 0
    overtime_amount: Decimal = 0
    gross_pay: Decimal
    tax_amount: Decimal = 0
    net_pay: Decimal

class PayrollCreate(PayrollBase):
    pass

class PayrollResponse(PayrollBase):
    payroll_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True