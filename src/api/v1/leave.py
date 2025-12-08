from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from src.models.session import get_db
from src.services.leave_service import LeaveService, ManagerService, HRExecutiveService
from src.schemas.leave import LeaveCreate, LeaveResponse, LeaveBalance, ManagerLeaveCreate, ManagerLeaveResponse, ManagerBalanceResponse, HRExecutiveLeaveCreate, HRExecutiveLeaveResponse, HRExecutiveBalanceResponse
from src.models.leave import Leave

router = APIRouter()

# Employee Leave Routes
@router.post("/leave/apply", response_model=LeaveResponse, tags=["Leave Management"])
def apply_leave(leave: LeaveCreate, db: Session = Depends(get_db)):
    try:
        return LeaveService.create_leave(db, leave)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leave/history/{employee_id}", response_model=List[LeaveResponse], tags=["Leave Management"])
def get_leave_history(employee_id: str, db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": employee_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="Employee not found")
        designation = emp_result[0]
        if designation and any(role in designation.lower() for role in ['manager', 'executive', 'admin']):
            raise HTTPException(status_code=403, detail="Access denied. This endpoint is only for employees.")
        return LeaveService.get_leaves(db, employee_id=employee_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leave/pending/{manager_id}", response_model=List[LeaveResponse], tags=["Leave Management"])
def get_pending_leaves_for_manager(manager_id: str, db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": manager_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="Manager not found")
        designation = emp_result[0]
        if designation and 'manager' not in designation.lower():
            raise HTTPException(status_code=403, detail="Access denied. This endpoint is only for managers.")
        return LeaveService.get_pending_approvals(db, manager_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/leave/approve/{leave_id}", response_model=LeaveResponse, tags=["Leave Management"])
def approve_reject_leave(leave_id: str, action: str = Query(...), manager_id: str = Query(...), db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": manager_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="Manager not found")
        designation = emp_result[0]
        if designation and 'manager' not in designation.lower():
            raise HTTPException(status_code=403, detail="Access denied. Only managers can approve leaves.")
        
        leave = db.query(Leave).filter(Leave.leave_id == int(leave_id)).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Leave not found")
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leave/balance/{employee_id}", response_model=LeaveBalance, tags=["Leave Management"])
def get_leave_balance(employee_id: str, db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": employee_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="Employee not found")
        result = db.execute(text("SELECT COUNT(*) FROM leave_management WHERE employee_id = :emp_id AND UPPER(status) = 'APPROVED'"), {"emp_id": employee_id}).fetchone()
        total_used = result[0] if result else 0
        return LeaveBalance(casual_leave=6, sick_leave=6, earned_leaves=6, total_leaves=18, employee_used_leaves=total_used, used_casual=0, used_sick=total_used, used_earned=0, remaining_casual=6, remaining_sick=6-total_used, remaining_earned=6)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Manager Leave Routes
@router.post("/manager/apply-leave", response_model=ManagerLeaveResponse, tags=["Manager to HR Executive"])
def manager_apply_leave(leave: ManagerLeaveCreate, db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": leave.manager_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="Manager not found")
        designation = emp_result[0]
        if designation and 'manager' not in designation.lower():
            raise HTTPException(status_code=403, detail="Access denied. Only managers can apply for leave through this endpoint.")
        return ManagerService.create_leave(db, leave)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/manager/history/{manager_id}", response_model=List[ManagerLeaveResponse], tags=["Manager to HR Executive"])
def get_manager_leave_history(manager_id: str, db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": manager_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="Manager not found")
        designation = emp_result[0]
        if designation and 'manager' not in designation.lower():
            raise HTTPException(status_code=403, detail="Access denied. This endpoint is only for managers.")
        return ManagerService.get_leave_history(db, manager_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/manager/pending/{hr_executive_id}", response_model=List[ManagerLeaveResponse], tags=["Manager to HR Executive"])
def get_pending_manager_leaves(hr_executive_id: str, db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": hr_executive_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="HR Executive not found")
        designation = emp_result[0]
        if designation and designation.lower() != 'hr executive':
            raise HTTPException(status_code=403, detail="Access denied. This endpoint is only for HR Executives.")
        return ManagerService.get_pending_approvals(db, hr_executive_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/manager/balance/{manager_id}", response_model=ManagerBalanceResponse, tags=["Manager to HR Executive"])
def get_manager_leave_balance(manager_id: str, db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": manager_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="Manager not found")
        designation = emp_result[0]
        if designation and 'manager' not in designation.lower():
            raise HTTPException(status_code=403, detail="Access denied. This endpoint is only for managers.")
        return ManagerService.get_leave_balance(db, manager_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/manager/approve/{leave_id}", tags=["Manager to HR Executive"])
def approve_reject_manager_leave(leave_id: str, action: str = Query(...), hr_executive_id: str = Query(...), db: Session = Depends(get_db)):
    try:
        result = ManagerService.approve_leave(db, leave_id, hr_executive_id, action)
        if not result:
            raise HTTPException(status_code=404, detail="Leave not found")
        return {"message": f"Leave {action}{'d' if action == 'approve' else 'ed'} successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# HR Executive Leave Routes
@router.post("/hr-executive/apply-leave", response_model=HRExecutiveLeaveResponse, tags=["HR Executive to HR Manager"])
def hr_executive_apply_leave(leave: HRExecutiveLeaveCreate, db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": leave.hr_executive_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="HR Executive not found")
        designation = emp_result[0]
        if designation and designation.lower() != 'hr executive':
            raise HTTPException(status_code=403, detail="Access denied. Only HR Executives can apply for leave through this endpoint.")
        return HRExecutiveService.create_leave(db, leave)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hr-executive/history/{hr_executive_id}", response_model=List[HRExecutiveLeaveResponse], tags=["HR Executive to HR Manager"])
def get_hr_executive_leave_history(hr_executive_id: str, db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": hr_executive_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="HR Executive not found")
        designation = emp_result[0]
        if designation and designation.lower() != 'hr executive':
            raise HTTPException(status_code=403, detail="Access denied. This endpoint is only for HR executives.")
        return HRExecutiveService.get_leave_history(db, hr_executive_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hr-executive/pending/{hr_manager_id}", response_model=List[HRExecutiveLeaveResponse], tags=["HR Executive to HR Manager"])
def get_pending_hr_executive_leaves(hr_manager_id: str, db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": hr_manager_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="HR Manager not found")
        designation = emp_result[0]
        if designation and designation.lower() != 'hr manager':
            raise HTTPException(status_code=403, detail="Access denied. This endpoint is only for HR Managers.")
        return HRExecutiveService.get_pending_approvals(db, hr_manager_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hr-executive/balance/{hr_executive_id}", response_model=HRExecutiveBalanceResponse, tags=["HR Executive to HR Manager"])
def get_hr_executive_leave_balance(hr_executive_id: str, db: Session = Depends(get_db)):
    try:
        emp_result = db.execute(text("SELECT designation FROM employees WHERE employee_id = :emp_id"), {"emp_id": hr_executive_id}).fetchone()
        if not emp_result:
            raise HTTPException(status_code=404, detail="HR Executive not found")
        designation = emp_result[0]
        if designation and designation.lower() != 'hr executive':
            raise HTTPException(status_code=403, detail="Access denied. This endpoint is only for HR executives.")
        return HRExecutiveService.get_leave_balance(db, hr_executive_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/hr-executive/approve/{leave_id}", tags=["HR Executive to HR Manager"])
def approve_reject_hr_executive_leave(leave_id: str, action: str = Query(...), hr_manager_id: str = Query(...), db: Session = Depends(get_db)):
    try:
        result = HRExecutiveService.approve_leave(db, leave_id, hr_manager_id, action)
        if not result:
            raise HTTPException(status_code=404, detail="Leave not found")
        return {"message": f"Leave {action}{'d' if action == 'approve' else 'ed'} successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
