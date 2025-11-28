from sqlalchemy import Column, String, Integer, DateTime, Date, Numeric
from sqlalchemy.sql import func
from src.models.base import Base
from datetime import datetime

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    designation = Column(String(100))
    department = Column(String(100))
    hire_date = Column(Date)
    is_active = Column(String(10), default="Active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())