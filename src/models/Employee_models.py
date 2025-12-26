from sqlalchemy import (
    Column, String, Integer, Date, ForeignKey, Numeric, Time,
    TIMESTAMP, CheckConstraint, Computed, Text, DateTime, LargeBinary
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

# ============================================================
# 3. EMPLOYEES (MASTER TABLE)
# ============================================================

class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = {'extend_existing': True}

    employee_id = Column(String(50), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)

    department_id = Column(Integer, nullable=False)
    designation = Column(String(50), nullable=False)
    joining_date = Column(Date, nullable=False)
    reporting_manager = Column(String(50))
    email_id = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    location = Column(String(50))
    shift_id = Column(Integer, nullable=False)
    employment_type = Column(String(50), nullable=False)
    annual_ctc = Column(String(50), default="0")
    annual_leaves = Column(Integer, server_default='21')
    
    profile_photo = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships - using lambda to avoid circular imports
    personal_details = relationship("EmployeePersonalDetailsModel", back_populates="employee",
                                    cascade="all, delete-orphan", uselist=False)
    bank_details = relationship("BankDetails", back_populates="employee",
                                cascade="all, delete")
    documents = relationship("EmployeeDocuments", back_populates="employee")
    education = relationship("EducationalQualifications", back_populates="employee")
    work_experience = relationship("EmployeeWorkExperience", back_populates="employee")

    def delete(self, session):
        """Delete employee and all related records"""
        session.delete(self)
        session.commit()


# ============================================================
# 4. EMPLOYEE PERSONAL DETAILS
# ============================================================

class EmployeePersonalDetailsModel(Base):
    __tablename__ = "employee_personal_details"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, unique=True)
    date_of_birth = Column(Date)
    gender = Column(String(20))
    marital_status = Column(String(20))
    blood_group = Column(String(5))
    nationality = Column(String(50))
    employee_phone = Column(String(20))
    employee_email = Column(String(100))
    employee_alternate_phone = Column(String(20))
    employee_address = Column(String(255))
    emergency_full_name = Column(String(50))
    emergency_relationship = Column(String(50))
    emergency_primary_phone = Column(String(20))
    emergency_alternate_phone = Column(String(20))
    emergency_address = Column(String(150))
    city = Column(String(100))
    pincode = Column(String(20))
    country = Column(String(100))
    state = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee", back_populates="personal_details", foreign_keys=[employee_id])


# ============================================================
# 5. BANK DETAILS
# ============================================================

class BankDetails(Base):
    __tablename__ = "bank_details"

    bank_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id", ondelete="CASCADE"))
    account_number = Column(String(30), unique=True)
    account_holder_name = Column(String(50), nullable=False)
    ifsc_code = Column(String(20), nullable=False)
    bank_name = Column(String(100), nullable=False)
    branch = Column(String(150))
    account_type = Column(String(20))
    pan_number = Column(String(15))
    aadhaar_number = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("account_type IN ('Savings','Current')", name="check_account_type"),
        {'extend_existing': True}
    )

    employee = relationship("Employee", back_populates="bank_details")


# ============================================================
# 6. ASSETS
# ============================================================

class Assets(Base):
    __tablename__ = "assets"
    __table_args__ = {'extend_existing': True}

    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(String(50), unique=True)
    asset_name = Column(String(50), nullable=False)
    asset_type = Column(String(50), nullable=False)
    employee_id = Column(String(50), nullable=True)
    assigned_to = Column(String(100), nullable=True)
    status = Column(String(50), default="Available")
    condition = Column(String(50), nullable=True)
    purchase_date = Column(Date, nullable=True)
    value = Column(Numeric(12, 2), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


# ============================================================
# 8. EDUCATIONAL QUALIFICATIONS
# ============================================================

class EducationalQualifications(Base):
    __tablename__ = "educational_qualifications"
    __table_args__ = {'extend_existing': True}

    edu_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id", ondelete="CASCADE"))
    course_name = Column(String(150), nullable=False)
    institution_name = Column(String(200), nullable=False)
    specialization = Column(String(50))
    start_year = Column(Integer)
    end_year = Column(Integer)
    grade = Column(String(50))
    skill_name = Column(String(150))
    proficiency_level = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee", back_populates="education")


# ============================================================
# 9. EMPLOYEE DOCUMENTS
# ============================================================

class EmployeeDocuments(Base):
    __tablename__ = "employee_documents"
    __table_args__ = {'extend_existing': True}

    document_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id", ondelete="CASCADE"))
    document_name = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    upload_date = Column(Date, nullable=False)
    status = Column(String(50), default="Pending")
   
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee", back_populates="documents")




# ============================================================
# 11. SHIFT MASTER
# ============================================================

class ShiftMaster(Base):
    __tablename__ = "shift_master"
    __table_args__ = {'extend_existing': True}

    shift_id = Column(Integer, primary_key=True, autoincrement=True)
    shift_name = Column(String(150), nullable=False)
    shift_type = Column(String(100), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    working_days = Column(String(200), default="Monday-Friday")
    employees = Column(Integer, server_default='0')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

# ============================================================
# DEPARTMENTS TABLE
# ============================================================

class Department(Base):
    __tablename__ = "departments"
    __table_args__ = {'extend_existing': True}
    
    department_id = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String(100), nullable=False, unique=True)

class EmployeeWorkExperience(Base):
    __tablename__ = "employee_work_experience"
    __table_args__ = {'extend_existing': True}

    experience_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)

    experience_designation = Column(String(150), nullable=True)
    company_name = Column(String(200), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date)
    responsibilities = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship back to Employee
    employee = relationship("Employee", back_populates="work_experience")