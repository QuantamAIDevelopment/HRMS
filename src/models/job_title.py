from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func, select
from sqlalchemy.ext.hybrid import hybrid_property
from .base import Base

class JobTitle(Base):
    __tablename__ = "job_titles"
    __table_args__ = {'extend_existing': True}

    job_title_id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(100), nullable=False)
    job_description = Column(String(255))
    department = Column(String(30), nullable=False)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    employees = Column(Integer, server_default='0')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())