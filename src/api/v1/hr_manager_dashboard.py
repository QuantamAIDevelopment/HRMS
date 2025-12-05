from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from ...models.session import get_db
from ...services.dashboard_service import DashboardService
from ...schemas.dashboard import DashboardResponse

router = APIRouter()

def verify_hr_manager_role(employee_id: str, db: Session):
    result = db.execute(text(
        "SELECT designation FROM employees WHERE employee_id = :emp_id"
    ), {"emp_id": employee_id})
    
    employee = result.fetchone()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if "hr manager" not in employee.designation.lower():
        raise HTTPException(status_code=403, detail="Access denied. HR Manager role required.")

@router.get("/hr-manager/dashboard/{employee_id}", response_model=DashboardResponse)
def get_hr_manager_dashboard(employee_id: str, db: Session = Depends(get_db)):
    verify_hr_manager_role(employee_id, db)
    
    dashboard_service = DashboardService(db)
    dashboard_data = dashboard_service.get_dashboard_data(employee_id)
    
    if not dashboard_data:
        raise HTTPException(status_code=404, detail="HR Manager not found")
    
    return dashboard_data