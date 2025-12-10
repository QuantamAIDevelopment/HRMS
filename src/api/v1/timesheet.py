from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import text
from typing import List
from datetime import date

from src.models.session import get_db
from src.models.timesheet import Timesheet
from src.schemas.timesheet import TimesheetCreate, TimesheetResponse, TimesheetUpdate
from src.schemas.timesheet_status import TimesheetStatusUpdate

router = APIRouter()

@router.post("/", response_model=TimesheetResponse, status_code=status.HTTP_201_CREATED)
def create_timesheet(timesheet: TimesheetCreate, db: Session = Depends(get_db)):
    try:
        # Check if employee exists
        employee_exists = db.execute(
            text("SELECT employee_id FROM employees WHERE employee_id = :emp_id"),
            {"emp_id": timesheet.employee_id}
        ).fetchone()
        
        if not employee_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Employee {timesheet.employee_id} not found"
            )
        
        # Get employee's reporting manager
        manager_query = db.execute(
            text("SELECT reporting_manager FROM employees WHERE employee_id = :emp_id"),
            {"emp_id": timesheet.employee_id}
        ).fetchone()
        
        # Check if employee is a manager (has direct reports)
        is_manager = db.execute(
            text("SELECT COUNT(*) as count FROM employees WHERE reporting_manager = :emp_id"),
            {"emp_id": timesheet.employee_id}
        ).fetchone().count > 0
        
        timesheet_data = timesheet.dict(exclude_unset=True)
        timesheet_data["time_entry_id"] = Timesheet.generate_time_entry_id(db)
        
        if is_manager:
            timesheet_data["status"] = "PENDING_HR_APPROVAL"
            timesheet_data["approver_type"] = "HR_MANAGER"
        else:
            timesheet_data["status"] = "PENDING_MANAGER_APPROVAL"
            timesheet_data["approver_id"] = manager_query.reporting_manager if manager_query else None
            timesheet_data["approver_type"] = "MANAGER"
        
        db_timesheet = Timesheet(**timesheet_data)
        db.add(db_timesheet)
        db.commit()
        db.refresh(db_timesheet)
        return db_timesheet
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[TimesheetResponse])
def get_timesheets(db: Session = Depends(get_db)):
    timesheets = db.query(Timesheet).all()
    return timesheets

@router.get("/cards")
def get_timesheet_cards(db: Session = Depends(get_db)):
    """Get timesheet analytics cards"""
    query = text("""
        SELECT 
            SUM(hours) as total_hours,
            COUNT(DISTINCT time_entry_id) as tasks_logged,
            COUNT(DISTINCT project) as active_projects
        FROM time_entries
        WHERE status IN ('APPROVED', 'PENDING_MANAGER_APPROVAL', 'PENDING_HR_APPROVAL')
    """)
    result = db.execute(query).fetchone()
    return {
        "total_hours": float(result.total_hours) if result.total_hours else 0,
        "tasks_logged": result.tasks_logged or 0,
        "active_projects": result.active_projects or 0
    }


@router.put("/edit/{employee_id}", response_model=TimesheetResponse, status_code=status.HTTP_200_OK)
def edit_timesheet(employee_id: str, timesheet_update: TimesheetUpdate, entry_date: str = Query(...), db: Session = Depends(get_db)):
    """Edit timesheet entry by employee ID and entry date"""
    try:
        from datetime import datetime
        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                entry_date_obj = datetime.strptime(entry_date, fmt).date()
                break
            except ValueError:
                continue
        else:
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD or DD-MM-YYYY")
    
    try:
        timesheet = db.query(Timesheet).filter(
            Timesheet.employee_id == employee_id,
            Timesheet.entry_date == entry_date_obj
        ).first()
        
        if not timesheet:
            raise HTTPException(status_code=404, detail="Timesheet not found")
        
        # Update fields (exclude employee_id and entry_date to prevent violations)
        update_data = timesheet_update.dict(exclude_unset=True)
        update_data.pop('employee_id', None)
        update_data.pop('entry_date', None)
        update_data.pop('time_entry_id', None)
        
        for field, value in update_data.items():
            setattr(timesheet, field, value)
        
        db.commit()
        db.refresh(timesheet)
        return timesheet
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{employee_id}", response_model=TimesheetResponse)
def update_timesheet_status(employee_id: str, status_update: TimesheetStatusUpdate, db: Session = Depends(get_db)):
    try:
        timesheet = db.query(Timesheet).filter(Timesheet.employee_id == employee_id, Timesheet.entry_date == status_update.entry_date).first()
        if not timesheet:
            raise HTTPException(status_code=404, detail="Timesheet not found")
        
        # Update status and trigger updated_at
        db.query(Timesheet).filter(Timesheet.employee_id == employee_id, Timesheet.entry_date == status_update.entry_date).update({"status": status_update.status})
        
        db.commit()
        db.refresh(timesheet)
        return timesheet
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

