from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.deps import get_db

router = APIRouter()

@router.get("/check-components/{employee_id}/{month}")
def check_components(employee_id: str, month: str, db: Session = Depends(get_db)):
    from models.salary import PayrollSetup
    
    payroll_record = db.query(PayrollSetup).filter(
        PayrollSetup.employee_id == employee_id,
        PayrollSetup.month == month
    ).first()
    
    if not payroll_record:
        return {"error": "Payroll record not found"}
    
    return {
        "employee_id": employee_id,
        "month": month,
        "payroll_id": payroll_record.payroll_id,
        "salary_components_raw": payroll_record.salary_components,
        "salary_components_type": type(payroll_record.salary_components).__name__
    }