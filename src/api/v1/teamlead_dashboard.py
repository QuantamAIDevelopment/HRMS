from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
import logging

from ...models.session import get_db
from ...services.dashboard_service import DashboardService
from ...schemas.dashboard import DashboardResponse

logger = logging.getLogger(__name__)
router = APIRouter()

def verify_team_lead_role(employee_id: str, db: Session):
    from sqlalchemy import text
    result = db.execute(text(
        "SELECT designation FROM employees WHERE employee_id = :emp_id"
    ), {"emp_id": employee_id})
    
    employee = result.fetchone()
    if not employee or employee.designation.lower() != "team lead":
        raise HTTPException(status_code=403, detail="Access denied. Team Lead role required.")

@router.get("/teamlead/dashboard/{employee_id}", response_model=DashboardResponse)
def get_teamlead_dashboard(employee_id: str, db: Session = Depends(get_db)):
    verify_team_lead_role(employee_id, db)
    
    try:
        logger.info(f"Team Lead dashboard request for employee: {employee_id}")
        dashboard_service = DashboardService(db)
        dashboard_data = dashboard_service.get_dashboard_data(employee_id)
        
        if not dashboard_data:
            logger.warning(f"No dashboard data found for team lead: {employee_id}")
            raise HTTPException(status_code=404, detail="Team Lead not found")
        
        logger.info(f"Team Lead dashboard data successfully retrieved for employee: {employee_id}")
        return dashboard_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in team lead dashboard endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



