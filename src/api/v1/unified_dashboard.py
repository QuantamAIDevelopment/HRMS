from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from src.models.session import get_db
from src.services.dashboard_service import DashboardService
from src.schemas.dashboard import DashboardResponse

logger = logging.getLogger(__name__)
router = APIRouter()

def get_user_role(employee_id: str, db: Session) -> str:
    """Get employee role from database"""
    result = db.execute(text(
        "SELECT designation FROM employees WHERE employee_id = :emp_id"
    ), {"emp_id": employee_id})
    
    employee = result.fetchone()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    designation = employee.designation.lower()
    
    if "hr manager" in designation:
        return "hr_manager"
    elif "hr executive" in designation:
        return "hr_executive"
    elif "manager" in designation:
        return "manager"
    else:
        return "employee"

@router.get("/dashboard/{employee_id}", response_model=DashboardResponse)
def get_unified_dashboard(employee_id: str, db: Session = Depends(get_db)):
    """Unified dashboard endpoint with role-based access control"""
    try:
        logger.info(f"Dashboard request for employee: {employee_id}")
        
        # Get user role
        user_role = get_user_role(employee_id, db)
        
        # Get dashboard data
        dashboard_service = DashboardService(db)
        dashboard_data = dashboard_service.get_dashboard_data(employee_id)
        
        if not dashboard_data:
            logger.warning(f"No dashboard data found for employee: {employee_id}")
            raise HTTPException(status_code=404, detail="Employee not found")
        
        logger.info(f"Dashboard data successfully retrieved for {user_role}: {employee_id}")
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in dashboard endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")