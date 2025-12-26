from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, time
from src.api.deps import get_db
from src.models import Attendance

router = APIRouter()

@router.post("/punch-in/{employee_id}")
def punch_in(employee_id: str, db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        today = date.today()
        now = datetime.now()
        current_time = now.time()
        
        # Check if already punched in today
        result = db.execute(text(
            "SELECT COUNT(*) FROM attendance WHERE employee_id = :emp_id AND attendance_date = :today AND punch_out IS NULL"
        ), {"emp_id": employee_id, "today": today})
        
        if result.scalar() > 0:
            raise HTTPException(status_code=400, detail="Already punched in today")
        
        # Insert attendance record
        db.execute(text(
            "INSERT INTO attendance (employee_id, attendance_date, punch_in, status, created_at, updated_at) VALUES (:emp_id, :today, :punch_time, 'Present', NOW(), NOW())"
        ), {"emp_id": employee_id, "today": today, "punch_time": current_time})
        
        db.commit()
        
        return {"message": "Punched in successfully", "date": today, "time": current_time}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/punch-out/{employee_id}")
def punch_out(employee_id: str, db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        today = date.today()
        now = datetime.now()
        current_time = now.time()
        
        # Check if punched in today
        result = db.execute(text(
            "SELECT attendance_id, punch_in FROM attendance WHERE employee_id = :emp_id AND attendance_date = :today AND punch_out IS NULL"
        ), {"emp_id": employee_id, "today": today})
        
        record = result.fetchone()
        if not record:
            raise HTTPException(status_code=400, detail="No active punch-in found for today")
        
        attendance_id = record.attendance_id
        punch_in_time = record.punch_in
        
        # Calculate work hours
        punch_in_dt = datetime.combine(today, punch_in_time)
        punch_out_dt = datetime.combine(today, current_time)
        total_seconds = (punch_out_dt - punch_in_dt).total_seconds()
        work_hours = round(total_seconds / 3600, 2)
        
        # Update attendance record
        db.execute(text(
            "UPDATE attendance SET punch_out = :punch_out, work_hours = :hours, updated_at = NOW() WHERE attendance_id = :att_id"
        ), {"punch_out": current_time, "hours": work_hours, "att_id": attendance_id})
        
        db.commit()
        
        return {
            "message": "Punched out successfully", 
            "date": today, 
            "punch_out_time": current_time,
            "work_hours": work_hours
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-attendance/{employee_id}")
def get_recent_attendance(employee_id: str, db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        
        result = db.execute(text("""
            SELECT attendance_date, punch_in, punch_out, work_hours, status
            FROM attendance 
            WHERE employee_id = :emp_id 
            ORDER BY attendance_date DESC 
            LIMIT 10
        """), {"emp_id": employee_id})
        
        records = result.fetchall()
        
        attendance_list = []
        for record in records:
            attendance_list.append({
                "date": record.attendance_date,
                "punch_in": record.punch_in,
                "punch_out": record.punch_out,
                "work_hours": record.work_hours,
                "status": record.status
            })
        
        return {"recent_attendance": attendance_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))