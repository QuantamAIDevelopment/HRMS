from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.schemas.salary_structure import SalaryStructureRequest, SalaryStructureResponse
from src.schemas.component_request import ComponentRequest
from src.services.payroll_service import PayrollService

router = APIRouter()

@router.post("/salary-structure/", response_model=SalaryStructureResponse)
def create_salary_structure(
    request: SalaryStructureRequest, 
    db: Session = Depends(get_db)
):
    return PayrollService.create_salary_structure(db, request)

@router.post("/salary-structure/{employee_id}/earnings", response_model=SalaryStructureResponse)
def add_earnings_component(
    employee_id: str,
    request: ComponentRequest,
    db: Session = Depends(get_db)
):
    return PayrollService.add_earnings_component(db, employee_id, request)

@router.post("/salary-structure/{employee_id}/deductions", response_model=SalaryStructureResponse)
def add_deductions_component(
    employee_id: str,
    request: ComponentRequest,
    db: Session = Depends(get_db)
):
    return PayrollService.add_deductions_component(db, employee_id, request)

@router.put("/salary-structure/{employee_id}/component", response_model=SalaryStructureResponse)
def update_component(
    employee_id: str,
    request: ComponentRequest,
    db: Session = Depends(get_db)
):
    return PayrollService.update_component(db, employee_id, request)

@router.get("/employee/{employee_id}")
def get_employee_details(
    employee_id: str, 
    db: Session = Depends(get_db)
):
    return PayrollService.get_employee_details(db, employee_id)

@router.get("/employees")
def get_all_employees(
    db: Session = Depends(get_db)
):
    return PayrollService.get_all_employees(db)

@router.get("/employee/{employee_id}/summary")
def get_employee_summary(
    employee_id: str, 
    db: Session = Depends(get_db)
):
    return PayrollService.get_employee_summary(db, employee_id)