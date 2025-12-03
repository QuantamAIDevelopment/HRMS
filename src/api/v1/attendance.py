from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import date
from decimal import Decimal
from ...models.session import get_db
from ...models.hrms_models import Attendance, Employee, Department, PolicyMaster, LeaveManagement
from ...schemas.attendance import AttendanceResponse, AttendanceBreakdown, DailyAttendanceRecord

router = APIRouter()

@router.get("/attendance", response_model=List[AttendanceResponse])
def get_attendance(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
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
    
    if month:
        query = query.filter(extract('month', Attendance.attendance_date) == month)
    if year:
        query = query.filter(extract('year', Attendance.attendance_date) == year)
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

@router.get("/attendance/breakdown", response_model=AttendanceBreakdown)
def get_attendance_breakdown(
    employee_id: Optional[str] = Query(None),
    employee_name: Optional[str] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db)
):
    if not employee_id and not employee_name:
        raise HTTPException(status_code=400, detail="Either employee_id or employee_name is required")
    
    emp_query = db.query(Employee, Department.department_name).join(Department, Employee.department_id == Department.department_id)
    
    if employee_id:
        emp_query = emp_query.filter(Employee.employee_id == employee_id)
    elif employee_name:
        emp_query = emp_query.filter((Employee.first_name + ' ' + Employee.last_name).ilike(f"%{employee_name}%"))
    
    emp_result = emp_query.first()
    if not emp_result:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee, department_name = emp_result
    
    att_query = db.query(Attendance).filter(Attendance.employee_id == employee.employee_id)
    
    if month:
        att_query = att_query.filter(extract('month', Attendance.attendance_date) == month)
    if year:
        att_query = att_query.filter(extract('year', Attendance.attendance_date) == year)
    
    attendance_records = att_query.order_by(Attendance.attendance_date).all()
    
    present_days = sum(1 for r in attendance_records if r.status and r.status.lower() == 'present')
    late_days = sum(1 for r in attendance_records if r.status and r.status.lower() == 'late')
    absent_days = sum(1 for r in attendance_records if r.status and r.status.lower() == 'absent')
    half_days = sum(1 for r in attendance_records if r.status and r.status.lower() == 'half day')
    leave_days = sum(1 for r in attendance_records if r.status and r.status.lower() == 'leave')
    
    total_work_days = len(attendance_records)
    total_work_hours = sum(r.work_hours for r in attendance_records if r.work_hours) or Decimal(0)
    attendance_rate = ((present_days + late_days) / total_work_days * 100) if total_work_days > 0 else 0
    
    daily_records = [
        DailyAttendanceRecord(
            date=record.attendance_date,
            day=record.attendance_date.strftime('%a'),
            punch_in=record.punch_in,
            punch_out=record.punch_out,
            work_hours=record.work_hours,
            status=record.status
        )
        for record in attendance_records
    ]
    
    return AttendanceBreakdown(
        employee_id=employee.employee_id,
        employee_name=f"{employee.first_name} {employee.last_name}",
        department=department_name,
        total_work_days=total_work_days,
        present_days=present_days,
        absent_days=absent_days,
        late_days=late_days,
        half_days=half_days,
        leave_days=leave_days,
        attendance_rate=round(attendance_rate, 2),
        total_work_hours=total_work_hours,
        daily_records=daily_records
    )
