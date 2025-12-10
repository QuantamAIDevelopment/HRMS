from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class EmployeeWorkExperience(Base):
    __tablename__ = "employee_work_experience"
    __table_args__ = {'extend_existing': True}
    
    experience_id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False)
    experience_designation = Column(String(150), nullable=False)
    company_name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    


class ProfileEditRequest(Base):
    __tablename__ = "profile_edit_requests"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    requested_changes = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    old_value = Column(String(255))
    new_value = Column(String(255))
    status = Column(String(20), default="pending", nullable=False)
    manager_comments = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())