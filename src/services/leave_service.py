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
        emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": db_leave.employee_id}).fetchone()
        employee_name = emp_name[0] if emp_name else "Unknown"
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
        query = db.query(Leave)
        if employee_id:
            query = query.filter(Leave.employee_id == employee_id)
        if status:
            query = query.filter(Leave.status == status)
        leaves = query.order_by(Leave.leave_id.desc()).all()
        
        result = []
        for leave in leaves:
            emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": leave.employee_id}).fetchone()
            employee_name = emp_name[0] if emp_name else "Unknown"
            result.append(LeaveResponse(
                leave_id=leave.leave_id,
                employee_id=leave.employee_id,
                employee_name=employee_name,
                leave_type=leave.leave_type,
                start_date=leave.start_date,
                end_date=leave.end_date,
                reason=leave.reason,
                status=leave.status
            ))
        return result

    @staticmethod
    def get_pending_approvals(db: Session, approver_id: str) -> List[LeaveResponse]:
        employee_ids = db.execute(text("SELECT employee_id FROM employees WHERE designation NOT ILIKE '%Manager%' AND designation NOT ILIKE '%Executive%'")).fetchall()
        employee_id_list = [emp[0] for emp in employee_ids]
        if not employee_id_list:
            return []
        leaves = db.query(Leave).filter(Leave.employee_id.in_(employee_id_list), Leave.status.in_(["PENDING", "APPROVED", "REJECTED"])).all()
        
        result = []
        for leave in leaves:
            emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": leave.employee_id}).fetchone()
            employee_name = emp_name[0] if emp_name else "Unknown"
            result.append(LeaveResponse(
                leave_id=leave.leave_id,
                employee_id=leave.employee_id,
                employee_name=employee_name,
                leave_type=leave.leave_type,
                start_date=leave.start_date,
                end_date=leave.end_date,
                reason=leave.reason,
                status=leave.status
            ))
        return result

    @staticmethod
    def approve_leave(db: Session, leave_id: str, approver_id: str, approver_role: str, action: str, comments: Optional[str] = None) -> Optional[LeaveResponse]:
        leave = db.query(Leave).filter(Leave.leave_id == int(leave_id)).first()
        if not leave:
            return None
        leave.status = "APPROVED" if action.lower() == "approve" else "REJECTED"
        db.commit()
        db.refresh(leave)
        emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": leave.employee_id}).fetchone()
        employee_name = emp_name[0] if emp_name else "Unknown"
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
        emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": db_leave.employee_id}).fetchone()
        manager_name = emp_name[0] if emp_name else "Unknown"
        return ManagerLeaveResponse(leave_id=db_leave.leave_id, manager_id=db_leave.employee_id, manager_name=manager_name, leave_type=db_leave.leave_type, start_date=db_leave.start_date, end_date=db_leave.end_date, reason=db_leave.reason, status=db_leave.status, approved_by=None, comments=None)

    @staticmethod
    def get_leave_history(db: Session, manager_id: str) -> List[ManagerLeaveResponse]:
        leaves = db.query(Leave).filter(Leave.employee_id == manager_id).order_by(Leave.leave_id.desc()).all()
        result = []
        for l in leaves:
            emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": l.employee_id}).fetchone()
            manager_name = emp_name[0] if emp_name else "Unknown"
            result.append(ManagerLeaveResponse(leave_id=l.leave_id, manager_id=l.employee_id, manager_name=manager_name, leave_type=l.leave_type, start_date=l.start_date, end_date=l.end_date, reason=l.reason, status=l.status, approved_by=None, comments=None))
        return result

    @staticmethod
    def get_leave_balance(db: Session, manager_id: str) -> ManagerBalanceResponse:
        emp_result = db.execute(text("SELECT employee_total_leaves FROM employees WHERE employee_id = :emp_id"), {"emp_id": manager_id}).fetchone()
        total_leaves = emp_result[0] if emp_result and emp_result[0] else 31
        each_leave = total_leaves // 3
        
        casual_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) LIKE '%casual%'"), {"emp_id": manager_id}).fetchone()[0] or 0
        sick_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) LIKE '%sick%'"), {"emp_id": manager_id}).fetchone()[0] or 0
        earned_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) LIKE '%earned%'"), {"emp_id": manager_id}).fetchone()[0] or 0
        total_used = casual_used + sick_used + earned_used
        
        return ManagerBalanceResponse(manager_id=manager_id, casual_leave=each_leave, sick_leave=each_leave, earned_leaves=each_leave, total_leaves=total_leaves, employee_used_leaves=total_used, used_casual=casual_used, used_sick=sick_used, used_earned=earned_used, remaining_casual=each_leave - casual_used, remaining_sick=each_leave - sick_used, remaining_earned=each_leave - earned_used)

    @staticmethod
    def approve_leave(db: Session, leave_id: str, hr_executive_id: str, action: str, comments: Optional[str] = None) -> Optional[ManagerLeaveResponse]:
        leave = db.query(Leave).filter(Leave.leave_id == int(leave_id)).first()
        if not leave:
            return None
        leave.status = "APPROVED" if action.lower() == "approve" else "REJECTED"
        db.commit()
        db.refresh(leave)
        emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": leave.employee_id}).fetchone()
        manager_name = emp_name[0] if emp_name else "Unknown"
        return ManagerLeaveResponse(leave_id=leave.leave_id, manager_id=leave.employee_id, manager_name=manager_name, leave_type=leave.leave_type, start_date=leave.start_date, end_date=leave.end_date, reason=leave.reason, status=leave.status, approved_by=hr_executive_id, comments=comments)

    @staticmethod
    def get_pending_approvals(db: Session, hr_executive_id: str) -> List[ManagerLeaveResponse]:
        manager_ids = db.execute(text("SELECT employee_id FROM employees WHERE designation ILIKE '%Manager%' AND designation NOT ILIKE '%HR Manager%'")).fetchall()
        manager_id_list = [mgr[0] for mgr in manager_ids]
        if not manager_id_list:
            return []
        leaves = db.query(Leave).filter(Leave.employee_id.in_(manager_id_list), Leave.status.in_(["PENDING", "APPROVED", "REJECTED"])).all()
        
        result = []
        for l in leaves:
            emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": l.employee_id}).fetchone()
            manager_name = emp_name[0] if emp_name else "Unknown"
            result.append(ManagerLeaveResponse(leave_id=l.leave_id, manager_id=l.employee_id, manager_name=manager_name, leave_type=l.leave_type, start_date=l.start_date, end_date=l.end_date, reason=l.reason, status=l.status, approved_by=None, comments=None))
        return result


class HRExecutiveService:
    @staticmethod
    def create_leave(db: Session, leave: HRExecutiveLeaveCreate) -> HRExecutiveLeaveResponse:
        db_leave = Leave(employee_id=leave.hr_executive_id, leave_type=leave.leave_type, start_date=leave.start_date, end_date=leave.end_date, reason=leave.reason, status="PENDING")
        db.add(db_leave)
        db.commit()
        db.refresh(db_leave)
        emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": db_leave.employee_id}).fetchone()
        hr_executive_name = emp_name[0] if emp_name else "Unknown"
        return HRExecutiveLeaveResponse(leave_id=db_leave.leave_id, hr_executive_id=db_leave.employee_id, hr_executive_name=hr_executive_name, leave_type=db_leave.leave_type, start_date=db_leave.start_date, end_date=db_leave.end_date, reason=db_leave.reason, status=db_leave.status, approved_by=None, comments=None)

    @staticmethod
    def get_leave_history(db: Session, hr_executive_id: str) -> List[HRExecutiveLeaveResponse]:
        leaves = db.query(Leave).filter(Leave.employee_id == hr_executive_id).order_by(Leave.leave_id.desc()).all()
        result = []
        for l in leaves:
            emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": l.employee_id}).fetchone()
            hr_executive_name = emp_name[0] if emp_name else "Unknown"
            result.append(HRExecutiveLeaveResponse(leave_id=l.leave_id, hr_executive_id=l.employee_id, hr_executive_name=hr_executive_name, leave_type=l.leave_type, start_date=l.start_date, end_date=l.end_date, reason=l.reason, status=l.status, approved_by=None, comments=None))
        return result

    @staticmethod
    def get_leave_balance(db: Session, hr_executive_id: str) -> HRExecutiveBalanceResponse:
        emp_result = db.execute(text("SELECT employee_total_leaves FROM employees WHERE employee_id = :emp_id"), {"emp_id": hr_executive_id}).fetchone()
        total_leaves = emp_result[0] if emp_result and emp_result[0] else 47
        each_leave = total_leaves // 3
        
        casual_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) LIKE '%casual%'"), {"emp_id": hr_executive_id}).fetchone()[0] or 0
        sick_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) LIKE '%sick%'"), {"emp_id": hr_executive_id}).fetchone()[0] or 0
        earned_used = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND status = 'APPROVED' AND LOWER(leave_type) LIKE '%earned%'"), {"emp_id": hr_executive_id}).fetchone()[0] or 0
        total_used = casual_used + sick_used + earned_used
        
        return HRExecutiveBalanceResponse(hr_executive_id=hr_executive_id, casual_leave=each_leave, sick_leave=each_leave, earned_leaves=each_leave, total_leaves=total_leaves, employee_used_leaves=total_used, used_casual=casual_used, used_sick=sick_used, used_earned=earned_used, remaining_casual=each_leave - casual_used, remaining_sick=each_leave - sick_used, remaining_earned=each_leave - earned_used)

    @staticmethod
    def approve_leave(db: Session, leave_id: str, hr_manager_id: str, action: str, comments: Optional[str] = None) -> Optional[HRExecutiveLeaveResponse]:
        leave = db.query(Leave).filter(Leave.leave_id == int(leave_id)).first()
        if not leave:
            return None
        leave.status = "APPROVED" if action.lower() == "approve" else "REJECTED"
        db.commit()
        db.refresh(leave)
        emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": leave.employee_id}).fetchone()
        hr_executive_name = emp_name[0] if emp_name else "Unknown"
        return HRExecutiveLeaveResponse(leave_id=leave.leave_id, hr_executive_id=leave.employee_id, hr_executive_name=hr_executive_name, leave_type=leave.leave_type, start_date=leave.start_date, end_date=leave.end_date, reason=leave.reason, status=leave.status, approved_by=hr_manager_id, comments=comments)

    @staticmethod
    def get_pending_approvals(db: Session, hr_manager_id: str) -> List[HRExecutiveLeaveResponse]:
        hr_exec_ids = db.execute(text("SELECT employee_id FROM employees WHERE designation ILIKE '%HR Executive%'")).fetchall()
        hr_exec_id_list = [hr[0] for hr in hr_exec_ids]
        if not hr_exec_id_list:
            return []
        leaves = db.query(Leave).filter(Leave.employee_id.in_(hr_exec_id_list), Leave.status.in_(["PENDING", "APPROVED", "REJECTED"])).all()
        
        result = []
        for l in leaves:
            emp_name = db.execute(text("SELECT full_name FROM employees WHERE employee_id = :emp_id"), {"emp_id": l.employee_id}).fetchone()
            hr_executive_name = emp_name[0] if emp_name else "Unknown"
            result.append(HRExecutiveLeaveResponse(leave_id=l.leave_id, hr_executive_id=l.employee_id, hr_executive_name=hr_executive_name, leave_type=l.leave_type, start_date=l.start_date, end_date=l.end_date, reason=l.reason, status=l.status, approved_by=None, comments=None))
        return result