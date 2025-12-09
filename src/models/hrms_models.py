from sqlalchemy import Column, Integer, String, Date, Time, Text, Numeric, Boolean, DateTime, ForeignKey, CheckConstraint, Index, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .base import Base

class Department(Base):
    __tablename__ = 'departments'
    __table_args__ = {'extend_existing': True}
    department_id = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String(100), unique=True, nullable=False)

class ShiftMaster(Base):
    __tablename__ = 'shift_master'
    __table_args__ = {'extend_existing': True}
    shift_id = Column(Integer, primary_key=True, autoincrement=True)
    shift_name = Column(String(150), nullable=False)
    shift_type = Column(String(100), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    working_days = Column(String(200), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Employee(Base):
    __tablename__ = 'employees'
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
    shift_id = Column(Integer, ForeignKey('shift_master.shift_id'))
    employee_type = Column(String(50))
    profile_photo = Column(String(255))
    annual_leaves = Column(Integer, server_default='21')
    annual_ctc = Column(Numeric(12, 2))
    active_status = Column(String(20), server_default='Active')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        Index('idx_employees_department', 'department_id'),
        Index('idx_employees_shift', 'shift_id'),
        {'extend_existing': True}
    )

class EmployeePersonalDetail(Base):
    __tablename__ = 'employee_personal_details'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id', ondelete='CASCADE'), unique=True, nullable=False)
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

class BankDetail(Base):
    __tablename__ = 'bank_details'
    bank_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id', ondelete='CASCADE'), nullable=False)
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
    __table_args__ = (
        CheckConstraint("account_type IN ('Savings','Current')", name='check_account_type'),
        {'extend_existing': True}
    )

class Asset(Base):
    __tablename__ = 'assets'
    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(String(50), unique=True)
    asset_name = Column(String(50), nullable=False)
    asset_type = Column(String(50), nullable=False)
    assigned_employee_id = Column(String(50), ForeignKey('employees.employee_id', ondelete='SET NULL'))
    status = Column(String(50), server_default='Available')
    condition = Column(String(50), server_default='Good')
    purchase_date = Column(Date)
    value = Column(Numeric(12, 2))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        CheckConstraint("status IN ('Assigned','Available','Maintenance')", name='check_status'),
        CheckConstraint("condition IN ('Excellent','Good','Fair')", name='check_condition'),
        Index('idx_assets_employee', 'assigned_employee_id'),
        {'extend_existing': True}
    )

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

class EducationalQualification(Base):
    __tablename__ = 'educational_qualifications'
    edu_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id', ondelete='CASCADE'), nullable=False)
    course_name = Column(String(150), nullable=False)
    institution_name = Column(String(200), nullable=False)
    specialization = Column(String(50))
    start_year = Column(Integer)
    end_year = Column(Integer)
    grade = Column(String(50))
    skill_name = Column(String(150))
    proficiency_level = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        Index('idx_edu_employee', 'employee_id'),
        {'extend_existing': True}
    )

class EmployeeDocument(Base):
    __tablename__ = 'employee_documents'
    __table_args__ = {'extend_existing': True}
    document_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id', ondelete='CASCADE'), nullable=False)
    document_name = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    upload_date = Column(Date, nullable=False)
    status = Column(String(50), server_default='Pending')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class EmployeeExpense(Base):
    __tablename__ = 'employee_expenses'
    __table_args__ = {'extend_existing': True}
    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id', ondelete='CASCADE'), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    amount = Column(Numeric(12, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class PayrollSetup(Base):
    __tablename__ = 'payroll_setup'
    payroll_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey('employees.employee_id', ondelete='CASCADE'), nullable=False)
    designation = Column(String(100), nullable=False)
    pay_cycle = Column(String(20), server_default='Monthly')
    basic_salary = Column(Numeric(12, 2), server_default='0')
    hra = Column(Numeric(12, 2), server_default='0')
    allowance = Column(Numeric(12, 2), server_default='0')
    bonus_percentage = Column(Numeric(5, 2), server_default='0')
    is_bonus_taxable = Column(Boolean, server_default='false')
    is_allowance_taxable = Column(Boolean, server_default='false')
    is_hra_taxable = Column(Boolean, server_default='false')
    is_basic_taxable = Column(Boolean, server_default='false')
    provident_fund_percentage = Column(Numeric(5, 2), server_default='0')
    professional_tax = Column(Numeric(12, 2), server_default='0')
    income_tax = Column(Numeric(12, 2), server_default='0')
    lop_amount = Column(Numeric(12, 2), server_default='0')
    is_pf_locked = Column(Boolean, server_default='false')
    is_pt_locked = Column(Boolean, server_default='false')
    is_income_tax_auto = Column(Boolean, server_default='false')
    total_earnings = Column(Numeric(12, 2), server_default='0')
    total_deductions = Column(Numeric(12, 2), server_default='0')
    net_salary = Column(Numeric(12, 2), server_default='0')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        CheckConstraint("pay_cycle IN ('Monthly','Weekly','Biweekly')", name='check_pay_cycle'),
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