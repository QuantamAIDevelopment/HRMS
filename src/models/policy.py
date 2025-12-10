from sqlalchemy import Column, String, Float, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base
 
class Policy(Base):
    __tablename__ = "policy_master"
    __table_args__ = {'extend_existing': True}
   
    # Core Policy fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    working_hours_per_day = Column(Float, nullable=False)
    working_days_per_week = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=False)
   
    # Timing Policy
    grace_period_minutes = Column(Integer, nullable=False)
    mark_late_after_minutes = Column(Integer, nullable=False)
    half_day_hours = Column(Float, nullable=False)
    auto_deduct_for_absence = Column(Boolean, nullable=False)
   
    # Overtime Policy
    overtime_enabled = Column(Boolean, nullable=False)
    overtime_multiplier_weekdays = Column(Float, nullable=True)
    overtime_multiplier_weekend = Column(Float, nullable=True)
   
    # Tracking Policy
    require_check_in = Column(Boolean, nullable=False)
    require_check_out = Column(Boolean, nullable=False)