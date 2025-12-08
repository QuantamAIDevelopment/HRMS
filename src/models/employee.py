from sqlalchemy import Column, String, Integer
from src.models.base import Base

class Employee(Base):
    __tablename__ = "employees"
    
    employee_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    designation = Column(String, nullable=True)
    role = Column(String, nullable=True)
    manager_id = Column(String, nullable=True)
    department = Column(String, nullable=True)
    employee_total_leaves = Column(Integer, nullable=True)
