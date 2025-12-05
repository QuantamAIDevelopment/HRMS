from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.models.user import User
from src.models.education import EducationalQualification
from src.schemas.education import EducationCreate, EducationUpdate, EducationResponse
from typing import List

router = APIRouter()

@router.post("/education", response_model=EducationResponse)
def create_education(
    education: EducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_education = EducationalQualification(**education.dict())
    db.add(db_education)
    db.commit()
    db.refresh(db_education)
    return db_education

@router.get("/education/{employee_id}", response_model=List[EducationResponse])
def get_employee_education(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(EducationalQualification).filter(EducationalQualification.employee_id == employee_id).all()

@router.put("/education/{edu_id}", response_model=EducationResponse)
def update_education(
    edu_id: int,
    education_update: EducationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_education = db.query(EducationalQualification).filter(EducationalQualification.edu_id == edu_id).first()
    if not db_education:
        raise HTTPException(status_code=404, detail="Education record not found")
    
    for field, value in education_update.dict(exclude_unset=True).items():
        setattr(db_education, field, value)
    
    db.commit()
    db.refresh(db_education)
    return db_education

@router.delete("/education/{edu_id}")
def delete_education(
    edu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_education = db.query(EducationalQualification).filter(EducationalQualification.edu_id == edu_id).first()
    if not db_education:
        raise HTTPException(status_code=404, detail="Education record not found")
    
    db.delete(db_education)
    db.commit()
    return {"message": "Education record deleted successfully"}