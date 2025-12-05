from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
import logging

from ...models.session import get_db
from ...services.dashboard_service import DashboardService
from ...schemas.dashboard import DashboardResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard/{employee_id}", response_model=DashboardResponse)
def get_employee_dashboard(employee_id: str, db: Session = Depends(get_db)):
    try:
        logger.info(f"Dashboard request for employee: {employee_id}")
        dashboard_service = DashboardService(db)
        dashboard_data = dashboard_service.get_dashboard_data(employee_id)
        
        if not dashboard_data:
            logger.warning(f"No dashboard data found for employee: {employee_id}")
            raise HTTPException(status_code=404, detail="Employee not found")
        
        logger.info(f"Dashboard data successfully retrieved for employee: {employee_id}")
        return dashboard_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in dashboard endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

