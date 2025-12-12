from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.models.session import get_db
from src.services.employee_service import EmployeeService
from src.schemas.employee import DepartmentResponse

router = APIRouter(prefix="/departments", tags=["departments"])

@router.get("", response_model=list[DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    """Get all departments for dropdown filter"""
    
    departments = EmployeeService.get_all_departments(db=db)
    
    return [
        DepartmentResponse(department_name=dept.department_name)
        for dept in departments
    ]