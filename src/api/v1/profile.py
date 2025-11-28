from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...models.session import get_db
from ...models.employee_profile import Department, ShiftMaster

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    """Get all departments"""
    departments = db.query(Department).all()
    return departments

@router.get("/shifts")
def get_shifts(db: Session = Depends(get_db)):
    """Get all shifts"""
    shifts = db.query(ShiftMaster).all()
    return shifts