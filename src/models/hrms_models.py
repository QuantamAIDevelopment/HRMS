from sqlalchemy import (
    Column, String, Integer, Date, ForeignKey, Numeric, Time,
    TIMESTAMP, CheckConstraint, Computed, Text, DateTime, LargeBinary,
    Boolean, Index, Float
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base

# ============================================================
# 3. EMPLOYEES (MASTER TABLE) - REMOVED TO AVOID CONFLICTS
# Use Employee from Employee_models.py instead
# ============================================================


# ============================================================
# 4. EMPLOYEE PERSONAL DETAILS - REMOVED TO AVOID CONFLICTS
# Use EmployeePersonalDetails from Employee_models.py instead
# ============================================================


# ============================================================
# SHIFT MASTER & DEPARTMENTS - USE FROM Employee_models.py
# ============================================================
# Removed duplicate definitions to avoid SQLAlchemy registry conflicts
# Use ShiftMaster and Department from Employee_models.py instead

# EmployeeWorkExperience - REMOVED TO AVOID CONFLICTS
# Use EmployeeWorkExperience from Employee_models.py instead

# BankDetails - REMOVED TO AVOID CONFLICTS
# Use BankDetails from Employee_models.py instead

# Assets - REMOVED TO AVOID CONFLICTS
# Use Assets from Employee_models.py instead

class Attendance(Base):
    __tablename__ = 'attendance'
    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id', ondelete='CASCADE'), nullable=False)
    attendance_date = Column(Date, nullable=False)
    punch_in = Column(Time)
    punch_out = Column(Time)
    work_hours = Column(Numeric(5, 2))
    status = Column(String(50))
    policy_id = Column(UUID(as_uuid=True), ForeignKey('policy_master.id'))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        Index('idx_attendance_emp', 'employee_id'),
        Index('idx_attendance_date', 'attendance_date'),
        {'extend_existing': True}
    )

# EducationalQualifications - REMOVED TO AVOID CONFLICTS
# Use EducationalQualifications from Employee_models.py instead

# EmployeeDocuments - REMOVED TO AVOID CONFLICTS
# Use EmployeeDocuments from Employee_models.py instead

class Expense(Base):
    __tablename__ = "employee_expenses"
    __table_args__ = {'extend_existing': True}
    
    expense_id = Column(Integer, primary_key=True, index=True)
    expense_code = Column(String(20), nullable=True)
    employee_id = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    receipt_url = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    @property
    def display_id(self):
        return f"E{self.expense_id}"

class PayrollSetup(Base):
    __tablename__ = "payroll_setup"

    payroll_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False, index=True)
    designation = Column(String(100), nullable=False)
    pay_cycle = Column(String(20), default="Monthly")

    basic_salary = Column(Numeric(12,2))
    hra = Column(Numeric(12,2))
    allowance = Column(Numeric(12,2))
  
    provident_fund_percentage = Column(Numeric(5,2))
    professional_tax = Column(Numeric(12,2))
    total_earnings = Column(Numeric(12,2))
    total_deductions = Column(Numeric(12,2))
    net_salary = Column(Numeric(12,2))

    pdf_path = Column(Text)
    month = Column(String(20), index=True)
    basic_salary_type = Column(String(50))
    hra_type = Column(String(50))
    allowance_type = Column(String(50))
    provident_fund_type = Column(String(50))
    professional_tax_type = Column(String(50))
    organization_name = Column(String(100))
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_employee_month', 'employee_id', 'month'),
        CheckConstraint('length(employee_id) > 0', name='check_employee_id_not_empty'),
        {'extend_existing': True}
    )

class LeaveManagement(Base):
    __tablename__ = 'leave_management'
    __table_args__ = {'extend_existing': True}
    leave_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id', ondelete='CASCADE'), nullable=False)
    leave_type = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    employee_used_leaves = Column(Integer, server_default='0')
    reason = Column(Text)
    status = Column(String(50), server_default='Pending')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class OnboardingProcess(Base):
    __tablename__ = 'onboarding_process'
    __table_args__ = {'extend_existing': True}
    onboarding_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id', ondelete='CASCADE'), nullable=False)
    name = Column(String(50), nullable=False)
    position = Column(String(50), nullable=False)
    department = Column(String(50), nullable=False)
    joining_date = Column(Date, nullable=False)
    shifts = Column(String(100))
    status = Column(String(50), server_default='Pending')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class JobTitle(Base):
    __tablename__ = 'job_titles'
    __table_args__ = {'extend_existing': True}
    job_title_id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String(150), nullable=False)
    job_description = Column(Text, nullable=False)
    department = Column(String(100), nullable=False)
    level = Column(String(50), nullable=False)
    salary_min = Column(Numeric(10, 2))
    salary_max = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class TimeEntry(Base):
    __tablename__ = "time_entries"
    __table_args__ = {'extend_existing': True}

    time_entry_id = Column(String(50), primary_key=True, index=True, nullable=False)
    employee_id = Column(String(50))
    entry_date = Column(Date)
    project = Column(String(150))
    task_description = Column(Text)
    hours = Column(Numeric(5, 2))
    status = Column(String(50), default="PENDING_MANAGER_APPROVAL")
    approver_id = Column(String(50))
    approver_type = Column(String(20))  # MANAGER, HR_MANAGER, HR_EXECUTIVE
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ComplianceDocument(Base):
    __tablename__ = 'compliance_documents_and_policy_management'
    document_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    uploaded_document = Column(Text)
    uploaded_by = Column(String(50), ForeignKey('employees.employee_id'), nullable=False)
    uploaded_on = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        CheckConstraint("category IN ('Policy','Compliance','Legal','Training')", name='check_category'),
        {'extend_existing': True}
    )

class PolicyMaster(Base):
    __tablename__ = 'policy_master'
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    working_hours_per_day = Column(Float, nullable=False)
    working_days_per_week = Column(Integer, nullable=False)
    is_active = Column(Boolean, server_default='false')
    grace_period_minutes = Column(Integer, nullable=False)
    mark_late_after_minutes = Column(Integer, nullable=False)
    half_day_hours = Column(Float, nullable=False)
    auto_deduct_for_absence = Column(Boolean, nullable=False)
    overtime_enabled = Column(Boolean, nullable=False)
    overtime_multiplier_weekdays = Column(Float)
    overtime_multiplier_weekend = Column(Float)
    require_check_in = Column(Boolean, nullable=False)
    require_check_out = Column(Boolean, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class EventHoliday(Base):
    __tablename__ = "events_holidays"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    subtitle = Column(String(255))
    type = Column(String(100))
    event_date = Column(Date)
    location = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())