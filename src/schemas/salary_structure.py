from pydantic import BaseModel
from typing import Dict, Any

class SalaryStructureRequest(BaseModel):
    employee_id: str
    pay_cycle_type: str
    month: str

class EarningsStructure(BaseModel):
    basic_salary: float
    basic_salary_type: str
    hra: float
    hra_type: str
    allowance: float
    allowance_type: str

class DeductionsStructure(BaseModel):
    provident_fund: float
    provident_fund_type: str
    professional_tax: float
    professional_tax_type: str

class SalaryStructureData(BaseModel):
    earnings: EarningsStructure
    deductions: DeductionsStructure

class SalaryStructureResponse(BaseModel):
    salary_structure: SalaryStructureData
    annual_ctc: float
    total_earnings: float
    total_deductions: float
    net_salary: float