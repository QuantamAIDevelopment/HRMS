from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from ...models.session import get_db
from ...models.shift import Shift
from ...schemas.shift import ShiftResponse, ShiftUpdate
from ...services.shift_service import ShiftService

router = APIRouter()


@router.get("/", response_model=List[ShiftResponse])
def get_shifts(db: Session = Depends(get_db)):
    shifts = db.query(Shift).all()
    result = []
    for shift in shifts:
        employee_count = db.execute(text("SELECT COUNT(*) FROM employees WHERE shift_id = :shift_id"), {"shift_id": shift.shift_id}).scalar()
        shift_data = {
            "shift_id": shift.shift_id,
            "shift_name": shift.shift_name,
            "shift_type": shift.shift_type,
            "start_time": shift.start_time,
            "end_time": shift.end_time,
            "working_days": shift.working_days,
            "employees": employee_count or 0,
            "created_at": shift.created_at,
            "updated_at": shift.updated_at
        }
        result.append(shift_data)
    return result

@router.get("/cards")
def get_shift_cards(db: Session = Depends(get_db)):
    # Get total shifts
    total_shifts = db.execute(text("SELECT COUNT(*) FROM shift_master")).scalar()
    
    # Get total employees with shifts
    total_employees = db.execute(text("SELECT COUNT(*) FROM employees WHERE shift_id IS NOT NULL")).scalar()
    
    # Get morning shift employees
    morning_shift = db.execute(text("""
        SELECT COUNT(e.employee_id) 
        FROM employees e 
        JOIN shift_master s ON e.shift_id = s.shift_id 
        WHERE LOWER(s.shift_type) = 'morning'
    """)).scalar()
    
    # Get night shift employees
    night_shift = db.execute(text("""
        SELECT COUNT(e.employee_id) 
        FROM employees e 
        JOIN shift_master s ON e.shift_id = s.shift_id 
        WHERE LOWER(s.shift_type) = 'night'
    """)).scalar()
    
    return {
        "total_shifts": total_shifts or 0,
        "total_employees": total_employees or 0,
        "morning_shift": morning_shift or 0,
        "night_shift": night_shift or 0
    }

@router.get("/{shift_name}", response_model=ShiftResponse)
def get_shift(shift_name: str, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.shift_name == shift_name).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    employee_count = db.execute(text("SELECT COUNT(*) FROM employees WHERE shift_id = :shift_id"), {"shift_id": shift.shift_id}).scalar()
    
    return {
        "shift_id": shift.shift_id,
        "shift_name": shift.shift_name,
        "shift_type": shift.shift_type,
        "start_time": shift.start_time,
        "end_time": shift.end_time,
        "working_days": shift.working_days,
        "employees": employee_count or 0,
        "created_at": shift.created_at,
        "updated_at": shift.updated_at
    }

@router.put("/{shift_name}", response_model=ShiftResponse)
def update_shift(shift_name: str, shift_update: ShiftUpdate, db: Session = Depends(get_db)):
    shift = ShiftService.update_shift_by_name(db, shift_name, shift_update)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift

@router.get("/{shift_name}/employees")
def get_employees_by_shift(shift_name: str, db: Session = Depends(get_db)):
    """Get all employees assigned to specific shift"""
    query = text("""
        SELECT 
            e.employee_id,
            CONCAT(e.first_name, ' ', e.last_name) as employee_name,
            d.department_name as department,
            s.start_time,
            s.end_time,
            s.working_days
        FROM employees e
        JOIN shift_master s ON e.shift_id = s.shift_id
        LEFT JOIN departments d ON e.department_id = d.department_id
        WHERE s.shift_name = :shift_name
        ORDER BY e.first_name, e.last_name
    """)
    result = db.execute(query, {"shift_name": shift_name}).fetchall()
    return [dict(row._mapping) for row in result]

@router.delete("/{shift_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shift(shift_name: str, db: Session = Depends(get_db)):
    success = ShiftService.delete_shift_by_name(db, shift_name)
    if not success:
        raise HTTPException(status_code=404, detail="Shift not found")