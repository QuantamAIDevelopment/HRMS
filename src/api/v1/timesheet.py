from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List
from datetime import date

from ...models.session import get_db
from ...models.timesheet import Timesheet
from ...schemas.timesheet import TimesheetCreate, TimesheetResponse, TimesheetUpdate
from ...schemas.timesheet_status import TimesheetStatusUpdate

router = APIRouter(prefix="/timesheets", tags=["timesheets"])

@router.post("/", response_model=TimesheetResponse, status_code=status.HTTP_201_CREATED)
def create_timesheet(timesheet: TimesheetCreate, db: Session = Depends(get_db)):
    timesheet_data = timesheet.dict(exclude_unset=True)
    timesheet_data["status"] = "PENDING"
    timesheet_data["time_entry_id"] = Timesheet.generate_time_entry_id(db)
    db_timesheet = Timesheet(**timesheet_data)
    db.add(db_timesheet)
    db.commit()
    db.refresh(db_timesheet)
    return db_timesheet

@router.get("/", response_model=List[TimesheetResponse])
def get_timesheets(db: Session = Depends(get_db)):
    timesheets = db.query(Timesheet).all()
    return timesheets

@router.get("/{employee_id}", response_model=List[TimesheetResponse])
def get_timesheet(employee_id: str, db: Session = Depends(get_db)):
    timesheets = db.query(Timesheet).filter(Timesheet.employee_id == employee_id).all()
    return timesheets

@router.put("/{employee_id}", response_model=TimesheetResponse)
def update_timesheet_status(employee_id: str, status_update: TimesheetStatusUpdate, db: Session = Depends(get_db)):
    timesheet = db.query(Timesheet).filter(Timesheet.employee_id == employee_id, Timesheet.entry_date == status_update.entry_date).first()
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    # Update status and trigger updated_at
    db.query(Timesheet).filter(Timesheet.employee_id == employee_id, Timesheet.entry_date == status_update.entry_date).update({"status": status_update.status})
    
    db.commit()
    db.refresh(timesheet)
    return timesheet

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timesheet(employee_id: str, db: Session = Depends(get_db)):
    timesheets = db.query(Timesheet).filter(Timesheet.employee_id == employee_id).all()
    if not timesheets:
        raise HTTPException(status_code=404, detail="No timesheets found for employee")
    
    for timesheet in timesheets:
        db.delete(timesheet)
    db.commit()