from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

class PayrollRecord(BaseModel):
    payroll_id: int
    employee_id: int
    pay_period_start: date
    pay_period_end: date
    basic_salary: Decimal
    allowances: Decimal
    deductions: Decimal
    overtime_hours: Decimal
    overtime_amount: Decimal
    gross_pay: Decimal
    tax_amount: Decimal
    net_pay: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PayrollSummary(BaseModel):
    total_employees: int
    total_gross_pay: Decimal
    total_deductions: Decimal
    total_net_pay: Decimal
    pay_period_start: date
    pay_period_end: date