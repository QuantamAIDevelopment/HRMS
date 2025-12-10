from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(String(20), primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    employee_id = Column(String, unique=True, index=True)
    role = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())