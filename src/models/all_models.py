from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Integer, Float, Text, Numeric, TIMESTAMP, Time, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Department(Base):
    __tablename__ = "departments"
    
    department_id = Column(Integer, primary_key=True)
    department_name = Column(String(100), unique=True, nullable=False)
    
    employees = relationship("Employee", back_populates="department")

class Employee(Base):
    __tablename__ = "employees"
    
    employee_id = Column(String(50), primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    department_id = Column(Integer, ForeignKey('departments.department_id'))
    designation = Column(String(50))
    joining_date = Column(Date)
    reporting_manager = Column(String(50), ForeignKey('employees.employee_id'))
    email_id = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20))
    location = Column(String(50))
    shift_id = Column(Integer)
    profile_photo = Column(String(255))
    annual_leaves = Column(Integer, default=20)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    
    department = relationship("Department", back_populates="employees")
    attendance_records = relationship("Attendance", back_populates="employee")
    personal_info = relationship("EmployeePersonal", back_populates="employee", uselist=False)
    expenses = relationship("Expense", back_populates="employee")
    leave_records = relationship("LeaveManagement", back_populates="employee")
    time_entries = relationship("TimeEntry", back_populates="employee")
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""

class EmployeePersonal(Base):
    __tablename__ = "employee_personal_details"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id'), unique=True, nullable=False)
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
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    
    employee = relationship("Employee", back_populates="personal_info")

class Attendance(Base):
    __tablename__ = "attendance"
    
    attendance_id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id'), nullable=False)
    attendance_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, server_default='NOW()')
    updated_at = Column(TIMESTAMP, server_default='NOW()')
    punch_in_time = Column(Time)
    punch_out_time = Column(Time)
    total_hours = Column(Numeric(5, 2))
    status = Column(String(20), server_default='Present')
    is_active = Column(Boolean, server_default='true')
    
    employee = relationship("Employee", back_populates="attendance_records")

class Expense(Base):
    __tablename__ = "employee_expenses"
    
    expense_id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id'), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    amount = Column(Numeric(12, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    expense_code = Column(String(50))
    receipt_url = Column(String(255))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    
    employee = relationship("Employee", back_populates="expenses")

class LeaveManagement(Base):
    __tablename__ = "leave_management"
    
    leave_id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id'), nullable=False)
    leave_type = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text)
    status = Column(String(50), default='Pending')
    employee_used_leaves = Column(Integer, default=0)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    
    employee = relationship("Employee", back_populates="leave_records")

class TimeEntry(Base):
    __tablename__ = "time_entries"
    
    time_entry_id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id'), nullable=False)
    entry_date = Column(Date, nullable=False)
    project = Column(String(150), nullable=False)
    task_description = Column(Text, nullable=False)
    hours = Column(Numeric(5, 2), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    
    employee = relationship("Employee", back_populates="time_entries")

class ShiftMaster(Base):
    __tablename__ = "shift_master"
    
    shift_id = Column(Integer, primary_key=True)
    shift_name = Column(String(100), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    break_duration = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

class ComplianceDocument(Base):
    __tablename__ = "compliance_documents_and_policy_management"
    
    document_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    uploaded_document = Column(Text)
    uploaded_by = Column(String(50), ForeignKey('employees.employee_id'), nullable=False)
    uploaded_on = Column(TIMESTAMP, server_default='NOW()')
    created_at = Column(TIMESTAMP, server_default='NOW()')
    updated_at = Column(TIMESTAMP, server_default='NOW()')
    
    uploader = relationship("Employee")

class EventHoliday(Base):
    __tablename__ = "events_holidays"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    subtitle = Column(String(255))
    type = Column(String(100))
    event_date = Column(Date)
    location = Column(String(255))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)