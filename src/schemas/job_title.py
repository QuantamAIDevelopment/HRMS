from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class JobTitleBase(BaseModel):
    job_title: str
    job_description: str
    department: str
    level: str
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None

class JobTitleCreate(JobTitleBase):
    pass

class JobTitleUpdate(BaseModel):
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    department: Optional[str] = None
    level: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None

class JobTitleResponse(JobTitleBase):
    job_title_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True