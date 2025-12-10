from sqlalchemy import Column, String, Integer, DateTime, Numeric, Date, Text, LargeBinary
from sqlalchemy.sql import func
from .base import BaseModel
from datetime import datetime

class Expense(BaseModel):
    __tablename__ = "employee_expenses"
    
    expense_id = Column(String(20),  primary_key=True, nullable=False)
    employee_id = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    receipt_url = Column(LargeBinary, nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def display_id(self):
        return f"E{self.id}"