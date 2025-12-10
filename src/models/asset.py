from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Numeric
from datetime import datetime
from .base import Base

class Asset(Base):
    __tablename__ = "assets"
    
    asset_id = Column(Integer, primary_key=True, index=True)
    asset_name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)
    serial_number = Column(String, unique=True, nullable=False)
    status = Column(String, default="Available")
    condition = Column(String, nullable=True)
    employee_id = Column(String, nullable=True)
    assigned_to = Column(String, nullable=True)
    purchase_date = Column(Date, nullable=True)
    value = Column(Numeric(12, 2), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
