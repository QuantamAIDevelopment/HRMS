from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.sql import func
from .base import Base

class JobTitle(Base):
    __tablename__ = "job_titles"

    job_title_id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(150), nullable=False)
    job_description = Column(Text, nullable=False)
    department = Column(String(100), nullable=False)
    level = Column(String(50), nullable=False)
    salary_min = Column(Numeric(10, 2))
    salary_max = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())