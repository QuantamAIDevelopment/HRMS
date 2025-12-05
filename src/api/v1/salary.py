from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.schemas.salary import SalaryCreate, SalaryResponse, PayslipResponse, PayrollSetupUpdate, SalaryComponentUpdate, ComponentDelete
from src.services.salary_service import SalaryService
from pydantic import BaseModel, Field
from typing import List
import json

router = APIRouter()



@router.delete("/delete-payslip/{payroll_id}/{employee_id}/{month}")
def delete_payslip(payroll_id: int, employee_id: str, month: str, db: Session = Depends(get_db)):
    """Delete payslip by payroll_id, employee_id, and month"""
    try:
        from src.models.salary import PayrollSetup
        
        payroll_record = db.query(PayrollSetup).filter(
            PayrollSetup.payroll_id == payroll_id,
            PayrollSetup.employee_id == employee_id,
            PayrollSetup.month == month
        ).first()
        
        if not payroll_record:
            raise HTTPException(status_code=404, detail="Payslip not found for the specified payroll_id, employee_id, and month")
        
        db.delete(payroll_record)
        db.commit()
        
        return {
            "message": "Payslip deleted successfully", 
            "payroll_id": payroll_id, 
            "employee_id": employee_id,
            "month": month
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting payslip: {str(e)}")

@router.get("/get-salary-summary/{employee_id}")
def get_salary_summary(employee_id: str, db: Session = Depends(get_db)):
    try:
        return SalaryService.get_salary_summary(db, employee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving salary summary: {str(e)}")



@router.get("/salaries")
def get_all_salaries(db: Session = Depends(get_db)):
    return SalaryService.get_all_salaries(db)

@router.get("/all-employee-ids")
def get_all_employee_ids(db: Session = Depends(get_db)):
    try:
        from src.models.Employee_models import Employee
        employees = db.query(Employee.employee_id).all()
        return {"employee_ids": [emp.employee_id for emp in employees]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving employee IDs: {str(e)}")

@router.get("/create-salary-structure/{employee_id}/{month}/{pay_cycle}")
def create_salary_structure_by_employee_id(
    employee_id: str, 
    month: str, 
    pay_cycle: str,
    db: Session = Depends(get_db)
):
    try:
        # Create salary structure for the specific employee
        salary_structure = SalaryService.create_salary_structure_by_employee_id(db, employee_id, month, pay_cycle)
        
        # Return only the salary structure
        return salary_structure
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating salary structure: {str(e)}")

class ComponentModel(BaseModel):
    component_name: str = Field(alias="Component_name")
    amount: float
    component_type: str = Field(alias="Component_type")
    
    class Config:
        populate_by_name = True

class SalaryStructureModel(BaseModel):
    employee_id: str
    pay_cycle: str
    pay_month: str
    earnings: List[ComponentModel] = []
    deductions: List[ComponentModel] = []

@router.post("/save-salary-structure")
def save_salary_structure(
    salary_data: SalaryStructureModel,
    db: Session = Depends(get_db)
):
    try:
        return SalaryService.save_salary_structure(db, salary_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving salary structure: {str(e)}")

@router.get("/payslip/{employee_id}")
def get_employee_payslip(employee_id: str, month: str = Query(None), db: Session = Depends(get_db)):
    """Get employee payslip information"""
    try:
        result = SalaryService.get_employee_payslip(db, employee_id, month)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving payslip: {str(e)}")



@router.put("/update-salary-components")
def update_salary_components(
    update_data: SalaryComponentUpdate,
    db: Session = Depends(get_db)
):
    """Update salary components (earnings/deductions) by employee_id and month"""
    try:
        return SalaryService.update_salary_components(db, update_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating salary components: {str(e)}")

@router.get("/salary-history/{employee_id}")
def get_salary_history(employee_id: str, db: Session = Depends(get_db)):
    """Get salary history showing Month, Year, Basic Salary, Allowances, Deductions, Net Pay"""
    try:
        return SalaryService.get_salary_history(db, employee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving salary history: {str(e)}")

@router.delete("/delete-component/{employee_id}/{month}/{component_name}")
def delete_component_simple(
    employee_id: str,
    month: str,
    component_name: str,
    component_type: str = Query(..., description="earnings or deductions"),
    db: Session = Depends(get_db)
):
    """Delete component by path parameters"""
    try:
        delete_data = ComponentDelete(
            employee_id=employee_id,
            month=month,
            component_name=component_name,
            component_type=component_type
        )
        return SalaryService.delete_salary_component(db, delete_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting salary component: {str(e)}")






