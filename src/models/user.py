from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.sql import func
from src.models.base import Base

class User(Base):
    __tablename__ = "userss"
    
    user_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="EMPLOYEE")

    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
   