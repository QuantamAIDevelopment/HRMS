from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from ...models.session import get_db
from ...services.dashboard_service import DashboardService
from ...schemas.dashboard import DashboardResponse

router = APIRouter()

def verify_hr_executive_role(employee_id: str, db: Session):
    result = db.execute(text(
        "SELECT designation FROM employees WHERE employee_id = :emp_id"
    ), {"emp_id": employee_id})
    
    employee = result.fetchone()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if "hr executive" not in employee.designation.lower():
        raise HTTPException(status_code=403, detail="Access denied. HR Executive role required.")

@router.get("/hr-executive/dashboard/{employee_id}", response_model=DashboardResponse)
def get_hr_executive_dashboard(employee_id: str, db: Session = Depends(get_db)):
    verify_hr_executive_role(employee_id, db)
    
    dashboard_service = DashboardService(db)
    dashboard_data = dashboard_service.get_dashboard_data(employee_id)
    
    if not dashboard_data:
        raise HTTPException(status_code=404, detail="HR Executive not found")
    
    return dashboard_data