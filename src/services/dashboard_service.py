from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract, and_
from datetime import datetime, date, timedelta
from typing import Optional
import logging

from ..models.all_models import Employee, EmployeePersonal, Attendance, Expense, LeaveManagement, TimeEntry, Department
from ..schemas.dashboard import DashboardResponse, EmployeeProfile, AttendanceSummary, LeaveBalance as LeaveBalanceSchema, TimesheetSummary, ExpensesSummary, Birthday, Holiday as HolidaySchema, Document as DocumentSchema

logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_data(self, employee_id: str) -> Optional[DashboardResponse]:
        try:
            employee = self.db.query(Employee).filter(Employee.employee_id == employee_id).first()
            
            if not employee:
                return None

            return DashboardResponse(
                employee_profile=self._get_employee_profile(employee),
                attendance_summary=self._get_attendance_summary(employee_id),
                leave_balance=self._get_leave_balance(employee_id),
                timesheet_summary=self._get_timesheet_summary(employee_id),
                expenses_summary=self._get_expenses_summary(employee_id),
                birthdays_this_month=self._get_birthdays_this_month(),
                upcoming_holidays=self._get_upcoming_holidays(),
                policy_documents=self._get_policy_documents()
            )
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return None

    def _get_employee_profile(self, employee: Employee) -> EmployeeProfile:
        department_name = ""
        if employee.department_id:
            dept = self.db.query(Department).filter(Department.department_id == employee.department_id).first()
            if dept:
                department_name = dept.department_name
        
        return EmployeeProfile(
            employee_id=employee.employee_id or "",
            full_name=employee.full_name or "Unknown",
            role=employee.designation or "",
            department=department_name,
            email=employee.email_id or "",
            phone=employee.phone_number or "",
            date_of_joining=employee.joining_date or date.today()
        )

    def _get_attendance_summary(self, employee_id: str) -> AttendanceSummary:
        try:
            from sqlalchemy import text
            today = date.today()
            
            # Get current month attendance
            month_start = today.replace(day=1)
            total_working_days = self.db.execute(text(
                "SELECT COUNT(DISTINCT attendance_date) FROM attendance WHERE employee_id = :emp_id AND attendance_date >= :month_start AND attendance_date <= :today"
            ), {"emp_id": employee_id, "month_start": month_start, "today": today}).scalar() or 0
            
            present_days = self.db.execute(text(
                "SELECT COUNT(*) FROM attendance WHERE employee_id = :emp_id AND attendance_date >= :month_start AND attendance_date <= :today AND LOWER(status) = 'present'"
            ), {"emp_id": employee_id, "month_start": month_start, "today": today}).scalar() or 0
            
            # Calculate percentage
            attendance_percentage = (present_days / total_working_days * 100) if total_working_days > 0 else 0.0
            
            return AttendanceSummary(
                monthly_attendance_percentage=round(attendance_percentage, 1)
            )
        except Exception as e:
            logger.error(f"Error calculating attendance: {e}")
            return AttendanceSummary(
                monthly_attendance_percentage=0.0
            )

    def _get_leave_balance(self, employee_id: str) -> LeaveBalanceSchema:
        try:
            from sqlalchemy import text
            
            # Single query with GROUP BY to get annual leaves and used leaves by type and status
            result = self.db.execute(text(
                "SELECT e.annual_leaves, lm.leave_type, lm.status, COUNT(lm.leave_id) as used_count "
                "FROM employees e "
                "LEFT JOIN leave_management lm ON e.employee_id = lm.employee_id "
                "WHERE e.employee_id = :emp_id "
                "GROUP BY e.annual_leaves, lm.leave_type, lm.status"
            ), {"emp_id": employee_id}).fetchall()
            
            annual_leaves = 30
            casual_used = sick_used = earned_used = 0
            
            for row in result:
                if row.annual_leaves:
                    annual_leaves = row.annual_leaves
                if row.leave_type and row.status and row.status.lower() == 'approved':
                    leave_type = row.leave_type.lower()
                    if 'casual' in leave_type:
                        casual_used += row.used_count
                    elif 'sick' in leave_type:
                        sick_used += row.used_count
                    elif 'earned' in leave_type:
                        earned_used += row.used_count
            
            # Calculate remaining (equal distribution)
            leaves_per_type = annual_leaves // 3
            casual_remaining = max(0, leaves_per_type - casual_used)
            sick_remaining = max(0, leaves_per_type - sick_used)
            earned_remaining = max(0, leaves_per_type - earned_used)
            
            total_remaining = casual_remaining + sick_remaining + earned_remaining
            
            return LeaveBalanceSchema(
                total_remaining=total_remaining,
                casual=casual_remaining,
                sick=sick_remaining,
                earned=earned_remaining
            )
        except Exception as e:
            logger.error(f"Error fetching leave balance: {e}")
            return LeaveBalanceSchema(
                total_remaining=30,
                casual=10,
                sick=10,
                earned=10
            )

    def _get_timesheet_summary(self, employee_id: str) -> TimesheetSummary:
        try:
            from sqlalchemy import text
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            
            # Get week hours from time_entries
            result = self.db.execute(text(
                "SELECT COALESCE(SUM(hours), 0) FROM time_entries WHERE employee_id = :emp_id AND entry_date >= :week_start AND entry_date <= :today"
            ), {"emp_id": employee_id, "week_start": week_start, "today": today})
            week_hours = result.scalar() or 0
            
            return TimesheetSummary(
                total_hours_this_week=float(week_hours)
            )
        except Exception as e:
            logger.error(f"Error fetching timesheet: {e}")
            return TimesheetSummary(
                total_hours_this_week=0.0
            )

    def _get_expenses_summary(self, employee_id: str) -> ExpensesSummary:
        try:
            from sqlalchemy import text
            result = self.db.execute(text(
                "SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM employee_expenses WHERE employee_id = :emp_id AND LOWER(status) LIKE '%pending%'"
            ), {"emp_id": employee_id})
            
            data = result.fetchone()
            pending_count = data[0] or 0
            total_pending = float(data[1]) if data[1] else 0.0
            
            return ExpensesSummary(
                pending_expense_count=pending_count,
                total_pending_amount=total_pending
            )
        except Exception as e:
            logger.error(f"Error fetching expenses: {e}")
            return ExpensesSummary(
                pending_expense_count=0,
                total_pending_amount=0.0
            )

    def _get_birthdays_this_month(self) -> list[Birthday]:
        try:
            current_month = date.today().month
            employees_with_birthdays = self.db.query(Employee, EmployeePersonal).join(
                EmployeePersonal, Employee.employee_id == EmployeePersonal.employee_id
            ).filter(
                EmployeePersonal.date_of_birth.isnot(None),
                extract('month', EmployeePersonal.date_of_birth) == current_month
            ).all()
            
            birthdays = []
            for emp, personal in employees_with_birthdays:
                dept_name = "Unknown"
                if emp.department_id:
                    dept = self.db.query(Department).filter(Department.department_id == emp.department_id).first()
                    if dept:
                        dept_name = dept.department_name
                
                # Format birthday as "Monday, 25 December"
                formatted_date = personal.date_of_birth.strftime("%A, %d %B")
                
                birthdays.append(Birthday(
                    name=emp.full_name or "Unknown",
                    department=dept_name,
                    birthday_date=formatted_date
                ))
            
            return birthdays
        except Exception as e:
            logger.error(f"Error fetching birthdays: {e}")
            return []

    def _get_upcoming_holidays(self) -> list[HolidaySchema]:
        try:
            from sqlalchemy import text
            today = date.today()
            
            result = self.db.execute(text(
                "SELECT title, event_date FROM events_holidays WHERE event_date >= :today ORDER BY event_date LIMIT 5"
            ), {"today": today})
            
            holidays = []
            for row in result:
                # Format holiday date as "December 2025"
                formatted_date = row.event_date.strftime("%B %Y")
                
                holidays.append(HolidaySchema(
                    holiday_name=row.title,
                    holiday_date=formatted_date
                ))
            
            return holidays
        except Exception as e:
            logger.error(f"Error fetching holidays: {e}")
            return []

    def _get_policy_documents(self) -> list[DocumentSchema]:
        try:
            from sqlalchemy import text
            
            result = self.db.execute(text(
                "SELECT title, category FROM compliance_documents_and_policy_management ORDER BY uploaded_on DESC LIMIT 10"
            ))
            
            documents = []
            for row in result:
                documents.append(DocumentSchema(
                    title=row.title,
                    category=row.category
                ))
            
            return documents
        except Exception as e:
            logger.error(f"Error fetching policy documents: {e}")
            return []