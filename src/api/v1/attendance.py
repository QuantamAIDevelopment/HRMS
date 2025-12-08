from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import date
from decimal import Decimal
from ...models.session import get_db
from ...models.hrms_models import Attendance, Employee, Department, PolicyMaster, LeaveManagement
from ...schemas.attendance import AttendanceResponse, AttendanceRecord, AttendanceSummary, AttendanceBreakdown, DailyAttendanceRecord

router = APIRouter()

def get_current_employee():
    """Replace with actual authentication logic"""
    return {
        "employee_id": "EMP001",
        "designation": "HR Manager"
    }

def check_hr_access(current_employee: dict = Depends(get_current_employee)):
    """Check if user is HR Manager or HR Executive"""
    allowed_roles = ["HR Manager", "HR Executive"]
    if current_employee["designation"] not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only HR Manager and HR Executive can access attendance tracking."
        )
    return current_employee

@router.get("/attendance", response_model=AttendanceResponse)
def get_attendance(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db),
    current_employee: dict = Depends(check_hr_access)
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
        .select_from(Attendance)
        .join(Employee, Attendance.employee_id == Employee.employee_id)
        .join(Department, Employee.department_id == Department.department_id)
    )
    
    if month:
        query = query.filter(extract('month', Attendance.attendance_date) == month)
    if year:
        query = query.filter(extract('year', Attendance.attendance_date) == year)
    
    results = query.all()
    
    total_employees = db.query(func.count(func.distinct(Employee.employee_id))).scalar()
    
    present_count = sum(1 for r in results if r.status and r.status.lower() in ['present', 'late'])
    absent_count = sum(1 for r in results if r.status and r.status.lower() == 'absent')
    leave_count = sum(1 for r in results if r.status and r.status.lower() == 'leave')
    
    attendance_rate = (present_count / total_employees * 100) if total_employees > 0 else 0
    
    summary = AttendanceSummary(
        total_employees=total_employees,
        present=present_count,
        absent=absent_count,
        on_leave=leave_count,
        attendance_rate=round(attendance_rate, 2)
    )
    
    records = [
        AttendanceRecord(
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
    
    return AttendanceResponse(summary=summary, records=records)

@router.get("/attendance/breakdown", response_model=AttendanceBreakdown)
def get_attendance_breakdown(
    employee_id: Optional[str] = Query(None),
    employee_name: Optional[str] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db),
    current_employee: dict = Depends(check_hr_access)
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
