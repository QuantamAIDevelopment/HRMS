from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

class ExpenseBase(BaseModel):
    employee_id: str
    category: str
    description: str
    amount: Decimal
    expense_date: date

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    expense_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    @property
    def display_id(self):
        return f"E{self.expense_id}"
    
    class Config:
        from_attributes = True

class ExpenseStatusResponse(BaseModel):
    """Response schema for expense status summary"""
    total_expenses: float = 0
    pending_review: float = 0
    approved: float = 0
    rejected: float = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "Total Expenses": 2444,
                "Pending Review": 2444,
                "Approved": 0,
                "Rejected": 0
            }
        }