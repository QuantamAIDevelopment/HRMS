from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from src.models.session import get_db
from src.models.job_title import JobTitle
from src.schemas.job_title import JobTitleCreate, JobTitleResponse, JobTitleUpdate

router = APIRouter()



@router.post("/", response_model=JobTitleResponse, status_code=status.HTTP_201_CREATED)
def create_job_title(job_title: JobTitleCreate, db: Session = Depends(get_db)):
    db_job_title = JobTitle(**job_title.dict())
    db.add(db_job_title)
    db.commit()
    db.refresh(db_job_title)
    return db_job_title

@router.get("/cards")
def get_job_title_cards(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            COUNT(DISTINCT jt.job_title_id) as total_roles,
            COUNT(DISTINCT jt.department) as departments,
            SUM(jt.employees) as total_employees
        FROM job_titles jt
    """)
    result = db.execute(query).fetchone()
    return dict(result._mapping)


@router.get("/", response_model=List[JobTitleResponse])
def get_job_titles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        job_titles = db.query(JobTitle).offset(skip).limit(limit).all()
        result = []
        for jt in job_titles:
            employee_count = db.execute(text("SELECT COUNT(*) FROM employees WHERE designation = :designation"), {"designation": jt.job_title}).scalar() or 0
            job_data = {
                "job_title_id": jt.job_title_id,
                "job_title": jt.job_title,
                "job_description": jt.job_description,
                "department": jt.department,
                "salary_min": jt.salary_min,
                "salary_max": jt.salary_max,
                "employees": employee_count,
                "created_at": jt.created_at,
                "updated_at": jt.updated_at
            }
            result.append(job_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

@router.get("/{job_title_name}/employees")
def get_employees_by_job_title(job_title_name: str, db: Session = Depends(get_db)):
    """Get all employees with specific job title/designation"""
    query = text("""
        SELECT 
            e.employee_id,
            CONCAT(e.first_name, ' ', e.last_name) as employee_name,
            d.department_name as department,
            e.designation,
            CONCAT(m.first_name, ' ', m.last_name) as manager_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.department_id
        LEFT JOIN employees m ON e.reporting_manager = m.employee_id
        WHERE e.designation = :job_title
        ORDER BY e.first_name, e.last_name
    """)
    result = db.execute(query, {"job_title": job_title_name}).fetchall()
    return [dict(row._mapping) for row in result]

@router.delete("/{job_title_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_title(job_title_name: str, db: Session = Depends(get_db)):
    job_title = db.query(JobTitle).filter(JobTitle.job_title == job_title_name).first()
    if not job_title:
        raise HTTPException(status_code=404, detail="Job title not found")
    
    try:
        db.delete(job_title)
        db.commit()
        return {"message": f"Job title '{job_title_name}' deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Cannot delete job title: {str(e)}")