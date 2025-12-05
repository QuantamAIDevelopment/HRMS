from sqlalchemy import Column, String, Integer, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Department(Base):
    __tablename__ = "departments"
    
    department_id = Column(Integer, primary_key=True)
    department_name = Column(String(100), nullable=False)

class Employee(Base):
    __tablename__ = "employees"
    
    employee_id = Column(String(20), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    full_name = Column(String(100))
    department_id = Column(Integer, nullable=False)
    designation = Column(String(100), nullable=False)
    joining_date = Column(Date, nullable=False)
    reporting_manager = Column(String(100))
    email_id = Column(String(100), unique=True, nullable=False, index=True)
    phone_number = Column(String(15))
    location = Column(String(100))
    shift_id = Column(Integer)
    profile_photo = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    annual_leaves = Column(Integer, default=21)
    annual_ctc = Column(Integer)
    active_status = Column(String(20), default="Active")

class PersonalDetails(Base):
    __tablename__ = "personal_details"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(15))
    blood_group = Column(String(5))
    marital_status = Column(String(20))

class BankDetails(Base):
    __tablename__ = "bank_details"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    bank_name = Column(String(100))
    account_number = Column(String(20))
    ifsc_code = Column(String(11))
    account_holder_name = Column(String(100))

class PayrollSetup(Base):
    __tablename__ = "payroll_setup"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    basic_salary = Column(Integer)
    hra = Column(Integer)
    transport_allowance = Column(Integer)
    medical_allowance = Column(Integer)
    pf_contribution = Column(Integer)

class LeaveManagement(Base):
    __tablename__ = "leave_management"
    
    leave_id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String(255))
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    employee_used_leaves = Column(Integer)