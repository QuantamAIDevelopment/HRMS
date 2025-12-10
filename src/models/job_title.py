from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func, select
from sqlalchemy.ext.hybrid import hybrid_property
from .base import Base

class JobTitle(Base):
    __tablename__ = "job_titles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    department = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())