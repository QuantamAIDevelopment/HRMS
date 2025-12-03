from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ...models.session import get_db
from ...models.hrms_models import Attendance, Employee, Department, PolicyMaster
from ...schemas.attendance import AttendanceResponse

router = APIRouter()

@router.get("/attendance", response_model=List[AttendanceResponse])
def get_attendance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = (
        db.query(
            Attendance.employee_id,
            (Employee.first_name + ' ' + Employee.last_name).label('employee_name'),
            Department.department_name.label('department'),
            Attendance.attendance_date.label('date'),
            Attendance.punch_in,
            Attendance.punch_out,
            Attendance.work_hours,
            Attendance.status
        )
        .join(Employee, Attendance.employee_id == Employee.employee_id)
        .join(Department, Employee.department_id == Department.department_id)
        .outerjoin(PolicyMaster, Attendance.policy_id == PolicyMaster.id)
    )
    
    if start_date:
        query = query.filter(Attendance.attendance_date >= start_date)
    if end_date:
        query = query.filter(Attendance.attendance_date <= end_date)
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)
    
    results = query.offset(skip).limit(limit).all()
    
    return [
        AttendanceResponse(
            employee_id=row.employee_id,
            employee_name=row.employee_name,
            department=row.department,
            date=row.date,
            punch_in=row.punch_in,
            punch_out=row.punch_out,
            work_hours=row.work_hours,
            status=row.status
        )
        for row in results
    ]
