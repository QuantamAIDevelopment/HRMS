from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal

class PayrollSetupBase(BaseModel):
    employee_id: int
    basic_salary: Decimal
    allowances: Decimal = 0
    deductions: Decimal = 0
    tax_rate: Decimal = 0
    overtime_rate: Decimal = 0
    is_active: bool = True

class PayrollSetupCreate(PayrollSetupBase):
    pass

class PayrollSetupResponse(PayrollSetupBase):
    setup_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True