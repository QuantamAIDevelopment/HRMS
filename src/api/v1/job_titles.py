from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...models.session import get_db
from ...models.job_title import JobTitle
from ...schemas.job_title import JobTitleCreate, JobTitleResponse, JobTitleUpdate

router = APIRouter(prefix="/job-titles", tags=["job-titles"])

@router.post("/", response_model=JobTitleResponse, status_code=status.HTTP_201_CREATED)
def create_job_title(job_title: JobTitleCreate, db: Session = Depends(get_db)):
    db_job_title = JobTitle(**job_title.dict())
    db.add(db_job_title)
    db.commit()
    db.refresh(db_job_title)
    return db_job_title

@router.get("/", response_model=List[JobTitleResponse])
def get_job_titles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    job_titles = db.query(JobTitle).offset(skip).limit(limit).all()
    return job_titles

@router.get("/{job_title_name}", response_model=JobTitleResponse)
def get_job_title(job_title_name: str, db: Session = Depends(get_db)):
    job_title = db.query(JobTitle).filter(JobTitle.job_title == job_title_name).first()
    if not job_title:
        raise HTTPException(status_code=404, detail="Job title not found")
    return job_title

@router.put("/{job_title_name}", response_model=JobTitleResponse)
def update_job_title(job_title_name: str, job_title_update: JobTitleUpdate, db: Session = Depends(get_db)):
    job_title = db.query(JobTitle).filter(JobTitle.job_title == job_title_name).first()
    if not job_title:
        raise HTTPException(status_code=404, detail="Job title not found")
    
    for field, value in job_title_update.dict(exclude_unset=True).items():
        setattr(job_title, field, value)
    
    db.commit()
    db.refresh(job_title)
    return job_title

@router.delete("/{job_title_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_title(job_title_name: str, db: Session = Depends(get_db)):
    job_title = db.query(JobTitle).filter(JobTitle.job_title == job_title_name).first()
    if not job_title:
        raise HTTPException(status_code=404, detail="Job title not found")
    
    db.delete(job_title)
    db.commit()