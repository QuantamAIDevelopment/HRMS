from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from models.session import get_db
from models.attendance import Attendance

router = APIRouter()

@router.post("/attendance/punch-in", tags=["Punch In Punch Out"])
def punch_in(employee_id: str, db: Session = Depends(get_db)):
    try:
        active = db.query(Attendance).filter(Attendance.employee_id == employee_id, Attendance.is_active == True).first()
        if active:
            raise HTTPException(status_code=400, detail="Already punched in")
        now = datetime.now()
        attendance = Attendance(employee_id=employee_id, attendance_date=now.date(), punch_in_time=now, is_active=True)
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return {"success": True, "message": "Punched in successfully", "attendance_id": attendance.attendance_id, "punch_in_time": attendance.punch_in_time}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/attendance/punch-out", tags=["Punch In Punch Out"])
def punch_out(employee_id: str, db: Session = Depends(get_db)):
    try:
        active = db.query(Attendance).filter(Attendance.employee_id == employee_id, Attendance.is_active == True).first()
        if not active:
            raise HTTPException(status_code=400, detail="No active session found")
        punch_out_time = datetime.now()
        time_diff = punch_out_time - active.punch_in_time
        total_hours = round(time_diff.total_seconds() / 3600, 2)
        active.punch_out_time = punch_out_time
        active.total_hours = total_hours
        active.is_active = False
        db.commit()
        return {"success": True, "message": "Punched out successfully", "attendance_id": active.attendance_id, "punch_out_time": punch_out_time, "total_hours": total_hours}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attendance/recent", tags=["Punch In Punch Out"])
def get_recent_attendance(employee_id: str, db: Session = Depends(get_db)):
    try:
        records = db.query(Attendance).filter(Attendance.employee_id == employee_id).order_by(Attendance.punch_in_time.desc()).limit(10).all()
        return [{"attendance_id": r.attendance_id, "employee_id": r.employee_id, "punch_in_time": r.punch_in_time, "punch_out_time": r.punch_out_time, "total_hours": r.total_hours, "is_active": r.is_active, "created_at": r.created_at} for r in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
