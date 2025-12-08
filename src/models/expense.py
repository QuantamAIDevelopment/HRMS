from sqlalchemy import Column, String, Integer, DateTime, Numeric, Date, Text
from sqlalchemy.sql import func
from models.base import Base
from datetime import datetime

class Expense(Base):
    __tablename__ = "employee_expenses"
    
    expense_id = Column(Integer, primary_key=True, index=True)
    expense_code = Column(String(20), nullable=True)
    employee_id = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    receipt_url = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def display_id(self):
        return f"E{self.expense_id}"