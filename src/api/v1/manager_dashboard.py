from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from ...models.session import get_db
from ...services.dashboard_service import DashboardService
from ...schemas.dashboard import DashboardResponse

router = APIRouter()

def verify_manager_role(employee_id: str, db: Session):
    result = db.execute(text(
        "SELECT designation FROM employees WHERE employee_id = :emp_id"
    ), {"emp_id": employee_id})
    
    employee = result.fetchone()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    designation = employee.designation.lower()
    if "manager" not in designation or "hr manager" in designation:
        raise HTTPException(status_code=403, detail="Access denied. Manager role required.")

@router.get("/manager/dashboard/{employee_id}", response_model=DashboardResponse)
def get_manager_dashboard(employee_id: str, db: Session = Depends(get_db)):
    verify_manager_role(employee_id, db)
    
    dashboard_service = DashboardService(db)
    dashboard_data = dashboard_service.get_dashboard_data(employee_id)
    
    if not dashboard_data:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    return dashboard_data