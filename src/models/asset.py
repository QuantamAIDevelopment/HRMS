from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = {'extend_existing': True}
    
    asset_id = Column(Integer, primary_key=True)
    serial_number = Column(String(50), unique=True)
    asset_name = Column(String(50), nullable=False)
    asset_type = Column(String(50), nullable=False)
    assigned_employee_id = Column(String(50), ForeignKey('employees.employee_id'))
    status = Column(String(50), default="Available")
    condition = Column(String(50), default="Good")
    purchase_date = Column(Date)
    value = Column(Numeric(12, 2))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
