from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from src.models.leave import Leave
from src.schemas.leave import LeaveCreate, LeaveResponse, LeaveBalance, ManagerLeaveCreate, ManagerLeaveResponse, ManagerBalanceResponse, HRExecutiveLeaveCreate, HRExecutiveLeaveResponse, HRExecutiveBalanceResponse

class LeaveService:
    @staticmethod
    def create_leave(db: Session, leave: LeaveCreate) -> LeaveResponse:
        db_leave = Leave(
            employee_id=leave.employee_id,
            leave_type=leave.leave_type,
            start_date=leave.start_date,
            end_date=leave.end_date,
            reason=leave.reason,
            status="PENDING"
        )
        db.add(db_leave)
        db.commit()
        db.refresh(db_leave)
        # Get employee name
        emp_name = db.execute(text("SELECT CONCAT(first_name, ' ', last_name) FROM employees WHERE employee_id = :emp_id"), {"emp_id": leave.employee_id}).fetchone()
        employee_name = emp_name[0] if emp_name else None
        
        return LeaveResponse(
            leave_id=db_leave.leave_id,
            employee_id=db_leave.employee_id,
            employee_name=employee_name,
            leave_type=db_leave.leave_type,
            start_date=db_leave.start_date,
            end_date=db_leave.end_date,
            reason=db_leave.reason,
            status=db_leave.status
        )

    @staticmethod
    def get_leaves(db: Session, employee_id: Optional[str] = None, status: Optional[str] = None) -> List[LeaveResponse]:
        if employee_id:
            leaves = db.execute(text("""
                SELECT l.leave_id, l.employee_id, l.leave_type, l.start_date, l.end_date, l.reason, l.status,
                       CONCAT(e.first_name, ' ', e.last_name) as employee_name
                FROM leave_management l 
                JOIN employees e ON l.employee_id = e.employee_id 
                WHERE l.employee_id = :emp_id
                ORDER BY l.leave_id DESC
            """), {"emp_id": employee_id}).fetchall()
        else:
            leaves = db.execute(text("""
                SELECT l.leave_id, l.employee_id, l.leave_type, l.start_date, l.end_date, l.reason, l.status,
                       CONCAT(e.first_name, ' ', e.last_name) as employee_name
                FROM leave_management l 
                JOIN employees e ON l.employee_id = e.employee_id 
                ORDER BY l.leave_id DESC
            """)).fetchall()
        
        return [LeaveResponse(
            leave_id=leave[0],
            employee_id=leave[1],
            employee_name=leave[7],
            leave_type=leave[2],
            start_date=leave[3],
            end_date=leave[4],
            reason=leave[5],
            status=leave[6]
        ) for leave in leaves]

    @staticmethod
    def get_pending_approvals(db: Session, approver_id: str) -> List[LeaveResponse]:
        leaves = db.execute(text("""
            SELECT l.leave_id, l.employee_id, l.leave_type, l.start_date, l.end_date, l.reason, l.status,
                   CONCAT(e.first_name, ' ', e.last_name) as employee_name
            FROM leave_management l 
            JOIN employees e ON l.employee_id = e.employee_id 
            WHERE UPPER(e.designation) NOT LIKE '%MANAGER%' 
            AND UPPER(e.designation) NOT LIKE '%EXECUTIVE%' 
            AND UPPER(e.designation) NOT LIKE '%ADMIN%'
            ORDER BY l.leave_id DESC
        """)).fetchall()
        
        return [LeaveResponse(
            leave_id=leave[0],
            employee_id=leave[1],
            employee_name=leave[7],
            leave_type=leave[2],
            start_date=leave[3],
            end_date=leave[4],
            reason=leave[5],
            status=leave[6]
        ) for leave in leaves]

    @staticmethod
    def approve_leave(db: Session, leave_id: str, approver_id: str, approver_role: str, action: str, comments: Optional[str] = None) -> Optional[LeaveResponse]:
        leave = db.query(Leave).filter(Leave.leave_id == int(leave_id)).first()
        if not leave:
            return None
        leave.status = "APPROVED" if action.lower() == "approve" else "REJECTED"
        db.commit()
        db.refresh(leave)
        # Get employee name
        emp_name = db.execute(text("SELECT CONCAT(first_name, ' ', last_name) FROM employees WHERE employee_id = :emp_id"), {"emp_id": leave.employee_id}).fetchone()
        employee_name = emp_name[0] if emp_name else None
        
        return LeaveResponse(
            leave_id=leave.leave_id,
            employee_id=leave.employee_id,
            employee_name=employee_name,
            leave_type=leave.leave_type,
            start_date=leave.start_date,
            end_date=leave.end_date,
            reason=leave.reason,
            status=leave.status
        )

class ManagerService:
    @staticmethod
    def create_leave(db: Session, leave: ManagerLeaveCreate) -> ManagerLeaveResponse:
        db_leave = Leave(employee_id=leave.manager_id, leave_type=leave.leave_type, start_date=leave.start_date, end_date=leave.end_date, reason=leave.reason, status="PENDING")
        db.add(db_leave)
        db.commit()
        db.refresh(db_leave)
        return ManagerLeaveResponse(leave_id=db_leave.leave_id, manager_id=db_leave.employee_id, leave_type=db_leave.leave_type, start_date=db_leave.start_date, end_date=db_leave.end_date, reason=db_leave.reason, status=db_leave.status, approved_by=None, comments=None)

    @staticmethod
    def get_leave_history(db: Session, manager_id: str) -> List[ManagerLeaveResponse]:
        leaves = db.execute(text("""
            SELECT l.leave_id, l.employee_id, l.leave_type, l.start_date, l.end_date, l.reason, l.status,
                   CONCAT(e.first_name, ' ', e.last_name) as manager_name
            FROM leave_management l 
            JOIN employees e ON l.employee_id = e.employee_id 
            WHERE l.employee_id = :manager_id
            ORDER BY l.leave_id DESC
        """), {"manager_id": manager_id}).fetchall()
        
        return [ManagerLeaveResponse(
            leave_id=l[0], 
            manager_id=l[1], 
            manager_name=l[7],
            leave_type=l[2], 
            start_date=l[3], 
            end_date=l[4], 
            reason=l[5], 
            status=l[6], 
            approved_by=None, 
            comments=None
        ) for l in leaves]

    @staticmethod
    def get_leave_balance(db: Session, manager_id: str) -> ManagerBalanceResponse:
        try:
            emp_result = db.execute(text("SELECT annual_leaves FROM employees WHERE employee_id = :emp_id"), {"emp_id": manager_id}).fetchone()
            total_leaves = int(emp_result[0]) if emp_result and emp_result[0] is not None else 31
        except Exception as e:
            db.rollback()
            total_leaves = 31
        
        each_leave = total_leaves // 3
        
        # Calculate used leaves by type
        casual_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) = 'casual'"), {"emp_id": manager_id}).fetchone()[0] or 0
        sick_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) = 'sick'"), {"emp_id": manager_id}).fetchone()[0] or 0
        earned_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) = 'earned'"), {"emp_id": manager_id}).fetchone()[0] or 0
        total_used = casual_used + sick_used + earned_used
        
        return ManagerBalanceResponse(
            manager_id=manager_id, 
            casual_leave=each_leave, 
            sick_leave=each_leave, 
            earned_leaves=each_leave, 
            total_leaves=total_leaves, 
            employee_used_leaves=total_used, 
            used_casual=casual_used, 
            used_sick=sick_used, 
            used_earned=earned_used, 
            remaining_casual=each_leave - casual_used, 
            remaining_sick=each_leave - sick_used, 
            remaining_earned=each_leave - earned_used
        )

    @staticmethod
    def approve_leave(db: Session, leave_id: str, hr_executive_id: str, action: str, comments: Optional[str] = None) -> Optional[ManagerLeaveResponse]:
        leave = db.query(Leave).filter(Leave.leave_id == int(leave_id)).first()
        if not leave:
            return None
        leave.status = "APPROVED" if action.lower() == "approve" else "REJECTED"
        db.commit()
        db.refresh(leave)
        return ManagerLeaveResponse(leave_id=leave.leave_id, manager_id=leave.employee_id, leave_type=leave.leave_type, start_date=leave.start_date, end_date=leave.end_date, reason=leave.reason, status=leave.status, approved_by=hr_executive_id, comments=comments)

    @staticmethod
    def get_pending_approvals(db: Session, hr_executive_id: str) -> List[ManagerLeaveResponse]:
        leaves = db.execute(text("""
            SELECT l.leave_id, l.employee_id, l.leave_type, l.start_date, l.end_date, l.reason, l.status,
                   CONCAT(e.first_name, ' ', e.last_name) as manager_name
            FROM leave_management l 
            JOIN employees e ON l.employee_id = e.employee_id 
            WHERE UPPER(e.designation) LIKE '%MANAGER%' AND UPPER(e.designation) NOT LIKE '%HR MANAGER%'
            ORDER BY l.leave_id DESC
        """)).fetchall()
        
        return [ManagerLeaveResponse(
            leave_id=l[0], 
            manager_id=l[1], 
            manager_name=l[7],
            leave_type=l[2], 
            start_date=l[3], 
            end_date=l[4], 
            reason=l[5], 
            status=l[6], 
            approved_by=None, 
            comments=None
        ) for l in leaves]


class HRExecutiveService:
    @staticmethod
    def create_leave(db: Session, leave: HRExecutiveLeaveCreate) -> HRExecutiveLeaveResponse:
        db_leave = Leave(employee_id=leave.hr_executive_id, leave_type=leave.leave_type, start_date=leave.start_date, end_date=leave.end_date, reason=leave.reason, status="PENDING")
        db.add(db_leave)
        db.commit()
        db.refresh(db_leave)
        return HRExecutiveLeaveResponse(leave_id=db_leave.leave_id, hr_executive_id=db_leave.employee_id, leave_type=db_leave.leave_type, start_date=db_leave.start_date, end_date=db_leave.end_date, reason=db_leave.reason, status=db_leave.status, approved_by=None, comments=None)

    @staticmethod
    def get_leave_history(db: Session, hr_executive_id: str) -> List[HRExecutiveLeaveResponse]:
        leaves = db.execute(text("""
            SELECT l.leave_id, l.employee_id, l.leave_type, l.start_date, l.end_date, l.reason, l.status,
                   CONCAT(e.first_name, ' ', e.last_name) as hr_executive_name
            FROM leave_management l 
            JOIN employees e ON l.employee_id = e.employee_id 
            WHERE l.employee_id = :hr_executive_id
            ORDER BY l.leave_id DESC
        """), {"hr_executive_id": hr_executive_id}).fetchall()
        
        return [HRExecutiveLeaveResponse(
            leave_id=l[0], 
            hr_executive_id=l[1], 
            hr_executive_name=l[7],
            leave_type=l[2], 
            start_date=l[3], 
            end_date=l[4], 
            reason=l[5], 
            status=l[6], 
            approved_by=None, 
            comments=None
        ) for l in leaves]

    @staticmethod
    def get_leave_balance(db: Session, hr_executive_id: str) -> HRExecutiveBalanceResponse:
        try:
            emp_result = db.execute(text("SELECT annual_leaves FROM employees WHERE employee_id = :emp_id"), {"emp_id": hr_executive_id}).fetchone()
            total_leaves = int(emp_result[0]) if emp_result and emp_result[0] is not None else 47
        except Exception as e:
            db.rollback()
            total_leaves = 47
        
        each_leave = total_leaves // 3
        
        # Calculate used leaves by type
        casual_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) = 'casual'"), {"emp_id": hr_executive_id}).fetchone()[0] or 0
        sick_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) = 'sick'"), {"emp_id": hr_executive_id}).fetchone()[0] or 0
        earned_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) = 'earned'"), {"emp_id": hr_executive_id}).fetchone()[0] or 0
        total_used = casual_used + sick_used + earned_used
        
        return HRExecutiveBalanceResponse(
            hr_executive_id=hr_executive_id, 
            casual_leave=each_leave, 
            sick_leave=each_leave, 
            earned_leaves=each_leave, 
            total_leaves=total_leaves, 
            employee_used_leaves=total_used, 
            used_casual=casual_used, 
            used_sick=sick_used, 
            used_earned=earned_used, 
            remaining_casual=each_leave - casual_used, 
            remaining_sick=each_leave - sick_used, 
            remaining_earned=each_leave - earned_used
        )

    @staticmethod
    def approve_leave(db: Session, leave_id: str, hr_manager_id: str, action: str, comments: Optional[str] = None) -> Optional[HRExecutiveLeaveResponse]:
        leave = db.query(Leave).filter(Leave.leave_id == int(leave_id)).first()
        if not leave:
            return None
        leave.status = "APPROVED" if action.lower() == "approve" else "REJECTED"
        db.commit()
        db.refresh(leave)
        return HRExecutiveLeaveResponse(leave_id=leave.leave_id, hr_executive_id=leave.employee_id, leave_type=leave.leave_type, start_date=leave.start_date, end_date=leave.end_date, reason=leave.reason, status=leave.status, approved_by=hr_manager_id, comments=comments)

    @staticmethod
    def get_pending_approvals(db: Session, hr_manager_id: str) -> List[HRExecutiveLeaveResponse]:
        leaves = db.execute(text("""
            SELECT l.leave_id, l.employee_id, l.leave_type, l.start_date, l.end_date, l.reason, l.status,
                   CONCAT(e.first_name, ' ', e.last_name) as hr_executive_name
            FROM leave_management l 
            JOIN employees e ON l.employee_id = e.employee_id 
            WHERE UPPER(e.designation) = 'HR EXECUTIVE'
            ORDER BY l.leave_id DESC
        """)).fetchall()
        
        return [HRExecutiveLeaveResponse(
            leave_id=l[0], 
            hr_executive_id=l[1], 
            hr_executive_name=l[7],
            leave_type=l[2], 
            start_date=l[3], 
            end_date=l[4], 
            reason=l[5], 
            status=l[6], 
            approved_by=None, 
            comments=None
        ) for l in leaves]
