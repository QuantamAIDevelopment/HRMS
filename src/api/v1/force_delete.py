from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.deps import get_db

router = APIRouter()

@router.delete("/force-delete/{employee_id}/{month}/{component_name}")
def force_delete_component(
    employee_id: str,
    month: str,
    component_name: str,
    db: Session = Depends(get_db)
):
    from models.salary import PayrollSetup
    
    # Get the record
    payroll_record = db.query(PayrollSetup).filter(
        PayrollSetup.employee_id == employee_id,
        PayrollSetup.month == month
    ).first()
    
    if not payroll_record:
        return {"error": "Payroll record not found"}
    
    # Set empty components to force deletion
    new_components = {
        "earnings": [
            c for c in payroll_record.salary_components.get("earnings", [])
            if c["component_name"] != component_name
        ],
        "deductions": [
            c for c in payroll_record.salary_components.get("deductions", [])
            if c["component_name"] != component_name
        ]
    }
    
    # Force update
    payroll_record.salary_components = new_components
    
    # Commit immediately
    db.commit()
    
    # Verify the change
    db.refresh(payroll_record)
    
    return {
        "message": "Component force deleted",
        "component_name": component_name,
        "basic_components": {
            "basic_salary": float(payroll_record.basic_salary),
            "hra": float(payroll_record.hra),
            "allowance": float(payroll_record.allowance),
            "provident_fund_percentage": float(payroll_record.provident_fund_percentage),
            "professional_tax": float(payroll_record.professional_tax)
        },
        "remaining_components": payroll_record.salary_components
    }