from sqlalchemy import Column, Integer, String, Time, DateTime
from sqlalchemy.sql import func
from .base import Base

class Shift(Base):
    __tablename__ = "shift_master"
    __table_args__ = {'extend_existing': True}

    shift_id = Column(Integer, primary_key=True, index=True)
    shift_name = Column(String(150), nullable=False)
    shift_type = Column(String(100), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    working_days = Column(String(200), nullable=False)
    employees = Column(Integer, server_default='0')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())