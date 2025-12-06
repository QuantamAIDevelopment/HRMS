from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobTitleBase(BaseModel):
    job_title: str
    job_description: Optional[str] = None
    department: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None

class JobTitleCreate(JobTitleBase):
    pass

class JobTitleUpdate(BaseModel):
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    department: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None

class JobTitleResponse(BaseModel):
    job_title_id: int
    job_title: str
    job_description: Optional[str] = None
    department: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    employees: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True