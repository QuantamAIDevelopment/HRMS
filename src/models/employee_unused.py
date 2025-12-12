from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class EmployeeUnused(Base):
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
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    personal_details = relationship("EmployeePersonalDetails", back_populates="employee", uselist=False)
    
    __table_args__ = (
        Index('idx_employees_department', 'department_id'),
        Index('idx_employees_shift', 'shift_id'),
        {'extend_existing': True}
    )
