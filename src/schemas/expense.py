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
    expense_code: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    @property
    def display_id(self):
        return f"E{self.expense_id}"
    
    class Config:
        from_attributes = True