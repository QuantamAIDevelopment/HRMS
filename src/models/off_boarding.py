from sqlalchemy import Column, Integer, String, Date, Text, Boolean, DateTime, DECIMAL
from sqlalchemy.sql import func
from .base import Base

class OffBoarding(Base):
    __tablename__ = "off_boarding"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), nullable=False)
    resignation_date = Column(Date)
    last_working_day = Column(Date)
    reason = Column(Text)
    status = Column(String(20), default="PENDING")  # PENDING, INITIATED, COMPLETED
    
    # Employee Details
    full_name = Column(String(150))
    email = Column(String(150))
    position = Column(String(100))
    department = Column(String(100))
    
    # Clearance Checklist
    it_asset_return = Column(Boolean, default=False)
    access_card_return = Column(Boolean, default=False)
    knowledge_transfer = Column(Boolean, default=False)
    exit_interview = Column(Boolean, default=False)
    final_settlement = Column(Boolean, default=False)
    
    # Additional Fields
    final_settlement_amount = Column(DECIMAL(12, 2))
    checklist_name = Column(String(150))
    description = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())