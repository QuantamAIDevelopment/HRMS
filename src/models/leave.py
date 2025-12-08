from sqlalchemy import Column, Integer, String, DateTime, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class Leave(Base):
    __tablename__ = "leave_management"
    
    leave_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, nullable=False)
    leave_type = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String, default="PENDING", nullable=False)

class EmployeeBalance(Base):
    __tablename__ = "employee_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, nullable=False)
    sick_leave_total = Column(Integer, default=6)
    casual_leave_total = Column(Integer, default=6)
    earned_leave_total = Column(Integer, default=6)
    sick_leave_used = Column(Integer, default=0)
    casual_leave_used = Column(Integer, default=0)
    earned_leave_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ManagerBalance(Base):
    __tablename__ = "manager_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(String, unique=True, nullable=False)
    sick_leave_total = Column(Integer, default=8)
    casual_leave_total = Column(Integer, default=8)
    earned_leave_total = Column(Integer, default=15)
    sick_leave_used = Column(Integer, default=0)
    casual_leave_used = Column(Integer, default=0)
    earned_leave_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TeamLeadBalance(Base):
    __tablename__ = "team_lead_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    team_lead_id = Column(String, unique=True, nullable=False)
    sick_leave_total = Column(Integer, default=10)
    casual_leave_total = Column(Integer, default=7)
    earned_leave_total = Column(Integer, default=21)
    sick_leave_used = Column(Integer, default=0)
    casual_leave_used = Column(Integer, default=0)
    earned_leave_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HRExecutiveBalance(Base):
    __tablename__ = "hr_executive_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    hr_executive_id = Column(String, unique=True, nullable=False)
    sick_leave_total = Column(Integer, default=12)
    casual_leave_total = Column(Integer, default=10)
    earned_leave_total = Column(Integer, default=25)
    sick_leave_used = Column(Integer, default=0)
    casual_leave_used = Column(Integer, default=0)
    earned_leave_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
