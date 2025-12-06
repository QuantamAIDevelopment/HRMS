from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Boolean, ForeignKey, Time, DECIMAL, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Department(Base):
    __tablename__ = "departments"
    
    department_id = Column(Integer, primary_key=True)
    department_name = Column(String(100), unique=True, nullable=False)

class ShiftMaster(Base):
    __tablename__ = "shift_master"
    
    shift_id = Column(Integer, primary_key=True)
    shift_name = Column(String(150), nullable=False)
    shift_type = Column(String(100), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    working_days = Column(String(200), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Employee(Base):
    __tablename__ = "employees"
    
    employee_id = Column(String(50), primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    designation = Column(String(50))
    joining_date = Column(Date)
    reporting_manager = Column(String(50), ForeignKey("employees.employee_id"))
    email_id = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20))
    location = Column(String(50))
    shift_id = Column(Integer, ForeignKey("shift_master.shift_id"))
    employee_type = Column(String(50))
    profile_photo = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department")
    shift = relationship("ShiftMaster")
    manager = relationship("Employee", remote_side=[employee_id])
    personal_details = relationship("EmployeePersonalDetails", back_populates="employee", uselist=False)
    bank_details = relationship("BankDetails", back_populates="employee")
    work_experience = relationship("EmployeeWorkExperience", back_populates="employee")
    assets = relationship("Asset", back_populates="assigned_employee")

class EmployeePersonalDetails(Base):
    __tablename__ = "employee_personal_details"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), unique=True, nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(20))
    marital_status = Column(String(20))
    blood_group = Column(String(5))
    nationality = Column(String(50))
    employee_email = Column(String(50))
    employee_phone = Column(String(20))
    employee_alternate_phone = Column(String(20))
    employee_address = Column(String(150))
    emergency_full_name = Column(String(50))
    emergency_relationship = Column(String(50))
    emergency_primary_phone = Column(String(20))
    emergency_alternate_phone = Column(String(20))
    emergency_address = Column(String(150))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="personal_details")

class BankDetails(Base):
    __tablename__ = "bank_details"
    
    bank_id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False)
    account_number = Column(String(30), unique=True)
    account_holder_name = Column(String(50), nullable=False)
    ifsc_code = Column(String(20), nullable=False)
    bank_name = Column(String(100), nullable=False)
    branch = Column(String(150))
    account_type = Column(String(20))
    pan_number = Column(String(15))
    aadhaar_number = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="bank_details")

class Asset(Base):
    __tablename__ = "assets"
    
    asset_id = Column(Integer, primary_key=True)
    serial_number = Column(String(50), unique=True)
    asset_name = Column(String(50), nullable=False)
    asset_type = Column(String(50), nullable=False)
    assigned_employee_id = Column(String(50), ForeignKey("employees.employee_id"))
    status = Column(String(50), default="Available")
    condition = Column(String(50), default="Good")
    purchase_date = Column(Date)
    value = Column(DECIMAL(12, 2))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    assigned_employee = relationship("Employee", back_populates="assets")

class EmployeeWorkExperience(Base):
    __tablename__ = "employee_work_experience"
    
    experience_id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False)
    experience_designation = Column(String(150), nullable=False)
    company_name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="work_experience")

class ProfileEditRequest(Base):
    __tablename__ = "profile_edit_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    requested_changes = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    old_value = Column(String(255))
    new_value = Column(String(255))
    status = Column(String(20), default="pending", nullable=False)
    manager_comments = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class EmployeeDocument(Base):
    __tablename__ = "employee_documents"

    document_name = Column(String(50), primary_key=True)
    employee_id = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    upload_date = Column(Date, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())