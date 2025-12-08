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
        return LeaveResponse(
            leave_id=db_leave.leave_id,
            employee_id=db_leave.employee_id,
            leave_type=db_leave.leave_type,
            start_date=db_leave.start_date,
            end_date=db_leave.end_date,
            reason=db_leave.reason,
            status=db_leave.status
        )

    @staticmethod
    def get_leaves(db: Session, employee_id: Optional[str] = None, status: Optional[str] = None) -> List[LeaveResponse]:
        query = db.query(Leave)
        if employee_id:
            query = query.filter(Leave.employee_id == employee_id)
        if status:
            query = query.filter(Leave.status == status)
        leaves = query.order_by(Leave.leave_id.desc()).all()
        return [LeaveResponse(
            leave_id=leave.leave_id,
            employee_id=leave.employee_id,
            leave_type=leave.leave_type,
            start_date=leave.start_date,
            end_date=leave.end_date,
            reason=leave.reason,
            status=leave.status
        ) for leave in leaves]

    @staticmethod
    def get_pending_approvals(db: Session, approver_id: str) -> List[LeaveResponse]:
        employee_ids = db.execute(text("SELECT employee_id FROM employees WHERE designation NOT LIKE '%Manager%' AND designation NOT LIKE '%Executive%'")).fetchall()
        employee_id_list = [emp[0] for emp in employee_ids]
        if not employee_id_list:
            return []
        leaves = db.query(Leave).filter(Leave.employee_id.in_(employee_id_list), Leave.status.in_(["PENDING", "APPROVED", "REJECTED"])).all()
        return [LeaveResponse(
            leave_id=leave.leave_id,
            employee_id=leave.employee_id,
            leave_type=leave.leave_type,
            start_date=leave.start_date,
            end_date=leave.end_date,
            reason=leave.reason,
            status=leave.status
        ) for leave in leaves]

    @staticmethod
    def approve_leave(db: Session, leave_id: str, approver_id: str, approver_role: str, action: str, comments: Optional[str] = None) -> Optional[LeaveResponse]:
        leave = db.query(Leave).filter(Leave.leave_id == int(leave_id)).first()
        if not leave:
            return None
        leave.status = "APPROVED" if action.lower() == "approve" else "REJECTED"
        db.commit()
        db.refresh(leave)
        return LeaveResponse(
            leave_id=leave.leave_id,
            employee_id=leave.employee_id,
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
        leaves = db.query(Leave).filter(Leave.employee_id == manager_id).order_by(Leave.leave_id.desc()).all()
        return [ManagerLeaveResponse(leave_id=l.leave_id, manager_id=l.employee_id, leave_type=l.leave_type, start_date=l.start_date, end_date=l.end_date, reason=l.reason, status=l.status, approved_by=None, comments=None) for l in leaves]

    @staticmethod
    def get_leave_balance(db: Session, manager_id: str) -> ManagerBalanceResponse:
        emp_result = db.execute(text("SELECT employee_total_leaves FROM employees WHERE employee_id = :emp_id"), {"emp_id": manager_id}).fetchone()
        total_leaves = emp_result[0] if emp_result and emp_result[0] else 31
        each_leave = total_leaves // 3
        
        result = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED'"), {"emp_id": manager_id}).fetchone()
        total_used = result[0] if result else 0
        
        return ManagerBalanceResponse(manager_id=manager_id, casual_leave=each_leave, sick_leave=each_leave, earned_leaves=each_leave, total_leaves=total_leaves, employee_used_leaves=total_used, used_casual=0, used_sick=total_used, used_earned=0, remaining_casual=each_leave, remaining_sick=each_leave - total_used, remaining_earned=each_leave)

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
        manager_ids = db.execute(text("SELECT employee_id FROM employees WHERE designation LIKE '%Manager%'")).fetchall()
        manager_id_list = [mgr[0] for mgr in manager_ids]
        if not manager_id_list:
            return []
        leaves = db.query(Leave).filter(Leave.employee_id.in_(manager_id_list), Leave.status.in_(["PENDING", "APPROVED", "REJECTED"])).all()
        return [ManagerLeaveResponse(leave_id=l.leave_id, manager_id=l.employee_id, leave_type=l.leave_type, start_date=l.start_date, end_date=l.end_date, reason=l.reason, status=l.status, approved_by=None, comments=None) for l in leaves]


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
        leaves = db.query(Leave).filter(Leave.employee_id == hr_executive_id).order_by(Leave.leave_id.desc()).all()
        return [HRExecutiveLeaveResponse(leave_id=l.leave_id, hr_executive_id=l.employee_id, leave_type=l.leave_type, start_date=l.start_date, end_date=l.end_date, reason=l.reason, status=l.status, approved_by=None, comments=None) for l in leaves]

    @staticmethod
    def get_leave_balance(db: Session, hr_executive_id: str) -> HRExecutiveBalanceResponse:
        emp_result = db.execute(text("SELECT employee_total_leaves FROM employees WHERE employee_id = :emp_id"), {"emp_id": hr_executive_id}).fetchone()
        total_leaves = emp_result[0] if emp_result and emp_result[0] else 47
        each_leave = total_leaves // 3
        
        result = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED'"), {"emp_id": hr_executive_id}).fetchone()
        total_used = result[0] if result else 0
        
        return HRExecutiveBalanceResponse(hr_executive_id=hr_executive_id, casual_leave=each_leave, sick_leave=each_leave, earned_leaves=each_leave, total_leaves=total_leaves, employee_used_leaves=total_used, used_casual=0, used_sick=total_used, used_earned=0, remaining_casual=each_leave, remaining_sick=each_leave - total_used, remaining_earned=each_leave)

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
        hr_exec_ids = db.execute(text("SELECT employee_id FROM employees WHERE designation = 'HR Executive'")).fetchall()
        hr_exec_id_list = [hr[0] for hr in hr_exec_ids]
        if not hr_exec_id_list:
            return []
        leaves = db.query(Leave).filter(Leave.employee_id.in_(hr_exec_id_list), Leave.status.in_(["PENDING", "APPROVED", "REJECTED"])).all()
        return [HRExecutiveLeaveResponse(leave_id=l.leave_id, hr_executive_id=l.employee_id, leave_type=l.leave_type, start_date=l.start_date, end_date=l.end_date, reason=l.reason, status=l.status, approved_by=None, comments=None) for l in leaves]
