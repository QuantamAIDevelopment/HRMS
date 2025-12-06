from pydantic import BaseModel
from typing import List, Optional

class PayrollComponent(BaseModel):
    component_name: str
    amount: float
    component_type: str
    original_percentage: Optional[float] = None

class PayrollTotals(BaseModel):
    total_earnings: float
    total_deductions: float
    net_salary: float

class RemainingComponents(BaseModel):
    earnings: List[PayrollComponent]
    deductions: List[PayrollComponent]

class PayrollComponentDeleteResponse(BaseModel):
    message: str
    payroll_id: int
    employee_id: str
    month: str
    deleted_component: str
    new_totals: PayrollTotals
    remaining_components: RemainingComponents

# Corrected: Transport Allowance should NOT be in remaining_components after deletion