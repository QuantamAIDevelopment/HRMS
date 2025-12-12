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

@router.post("/")
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
        is_manager_result = db.execute(
            text("SELECT COUNT(*) as count FROM employees WHERE reporting_manager = :emp_id"),
            {"emp_id": timesheet.employee_id}
        ).fetchone()
        is_manager = is_manager_result[0] > 0 if is_manager_result else False
        
        # Prepare data for insertion using raw SQL to match database schema
        if is_manager:
            status = "PENDING_HR_APPROVAL"
            approver_type = "HR_MANAGER"
            approver_id = None
        else:
            status = "PENDING_MANAGER_APPROVAL"
            approver_id = manager_query[0] if manager_query else None
            approver_type = "MANAGER"
        
        # Insert using raw SQL to handle SERIAL primary key
        insert_query = text("""
            INSERT INTO time_entries (employee_id, entry_date, project, task_description, hours, status, approver_id, approver_type)
            VALUES (:employee_id, :entry_date, :project, :task_description, :hours, :status, :approver_id, :approver_type)
            RETURNING time_entry_id, employee_id, entry_date, project, task_description, hours, status, approver_id, approver_type, created_at, updated_at
        """)
        
        result = db.execute(insert_query, {
            "employee_id": timesheet.employee_id,
            "entry_date": timesheet.entry_date,
            "project": timesheet.project,
            "task_description": timesheet.task_description,
            "hours": timesheet.hours,
            "status": status,
            "approver_id": approver_id,
            "approver_type": approver_type
        })
        
        db.commit()
        row = result.fetchone()
        
        return {
            "time_entry_id": row.time_entry_id,
            "employee_id": row.employee_id,
            "entry_date": row.entry_date,
            "project": row.project,
            "task_description": row.task_description,
            "hours": float(row.hours),
            "status": row.status,
            "approver_id": row.approver_id,
            "approver_type": row.approver_type,
            "created_at": row.created_at,
            "updated_at": row.updated_at
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def get_timesheets(db: Session = Depends(get_db)):
    query = text("SELECT * FROM time_entries ORDER BY created_at DESC")
    result = db.execute(query).fetchall()
    
    return [{
        "time_entry_id": row.time_entry_id,
        "employee_id": row.employee_id,
        "entry_date": row.entry_date,
        "project": row.project,
        "task_description": row.task_description,
        "hours": float(row.hours),
        "status": row.status,
        "approver_id": row.approver_id,
        "approver_type": row.approver_type,
        "created_at": row.created_at,
        "updated_at": row.updated_at
    } for row in result]

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


@router.put("/edit/{employee_id}", status_code=status.HTTP_200_OK)
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
        # Check if timesheet exists and get current status
        check_query = text("SELECT time_entry_id, status FROM time_entries WHERE employee_id = :emp_id AND entry_date = :entry_date")
        existing = db.execute(check_query, {"emp_id": employee_id, "entry_date": entry_date_obj}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Timesheet not found")
        
        # Update using raw SQL
        update_data = timesheet_update.dict(exclude_unset=True)
        update_data.pop('employee_id', None)
        update_data.pop('entry_date', None)
        update_data.pop('time_entry_id', None)
        
        if update_data:
            # If timesheet is being updated after submission, reset status to pending
            if existing.status in ["REJECTED", "APPROVED", "PENDING_MANAGER_APPROVAL", "PENDING_HR_APPROVAL"]:
                # Check if employee is a manager to determine correct pending status
                is_manager_result = db.execute(
                    text("SELECT COUNT(*) as count FROM employees WHERE reporting_manager = :emp_id"),
                    {"emp_id": employee_id}
                ).fetchone()
                is_manager = is_manager_result[0] > 0 if is_manager_result else False
                
                # Set appropriate pending status
                update_data["status"] = "PENDING_HR_APPROVAL" if is_manager else "PENDING_MANAGER_APPROVAL"
            
            set_clauses = []
            params = {"emp_id": employee_id, "entry_date": entry_date_obj}
            
            for field, value in update_data.items():
                set_clauses.append(f"{field} = :{field}")
                params[field] = value
            
            update_query = text(f"""
                UPDATE time_entries 
                SET {', '.join(set_clauses)}, updated_at = NOW()
                WHERE employee_id = :emp_id AND entry_date = :entry_date
                RETURNING *
            """)
            
            result = db.execute(update_query, params)
            db.commit()
            row = result.fetchone()
            
            return {
                "time_entry_id": row.time_entry_id,
                "employee_id": row.employee_id,
                "entry_date": row.entry_date,
                "project": row.project,
                "task_description": row.task_description,
                "hours": float(row.hours),
                "status": row.status,
                "approver_id": row.approver_id,
                "approver_type": row.approver_type,
                "created_at": row.created_at,
                "updated_at": row.updated_at
            }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{employee_id}")
def update_timesheet_status(employee_id: str, status_update: TimesheetStatusUpdate, db: Session = Depends(get_db)):
    try:
        # Check current status for resubmit logic
        check_query = text("SELECT status FROM time_entries WHERE employee_id = :emp_id AND entry_date = :entry_date")
        current = db.execute(check_query, {"emp_id": employee_id, "entry_date": status_update.entry_date}).fetchone()
        
        if not current:
            raise HTTPException(status_code=404, detail="Timesheet not found")
        
        final_status = status_update.status
        
        # Resubmit logic: if current status is REJECTED and new status is RESUBMIT
        if current.status == "REJECTED" and status_update.status == "RESUBMIT":
            # Check if employee is a manager to determine correct pending status
            is_manager_result = db.execute(
                text("SELECT COUNT(*) as count FROM employees WHERE reporting_manager = :emp_id"),
                {"emp_id": employee_id}
            ).fetchone()
            is_manager = is_manager_result[0] > 0 if is_manager_result else False
            
            # Set appropriate pending status
            final_status = "PENDING_HR_APPROVAL" if is_manager else "PENDING_MANAGER_APPROVAL"
        
        # Update using raw SQL
        update_query = text("""
            UPDATE time_entries 
            SET status = :status, updated_at = NOW()
            WHERE employee_id = :emp_id AND entry_date = :entry_date
            RETURNING *
        """)
        
        result = db.execute(update_query, {
            "status": final_status,
            "emp_id": employee_id,
            "entry_date": status_update.entry_date
        })
        
        row = result.fetchone()
        db.commit()
        
        return {
            "time_entry_id": row.time_entry_id,
            "employee_id": row.employee_id,
            "entry_date": row.entry_date,
            "project": row.project,
            "task_description": row.task_description,
            "hours": float(row.hours),
            "status": row.status,
            "approver_id": row.approver_id,
            "approver_type": row.approver_type,
            "created_at": row.created_at,
            "updated_at": row.updated_at
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

