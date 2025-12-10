from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.models.session import get_db
from src.core.security import require_hr_role, CurrentUser
from src.services.employee_service import EmployeeService
from src.schemas.employee import (
    EmployeeListResponse, 
    EmployeeDetailResponse, 
    EmployeeUpdate,
    EmployeeUpdateResponse,
    DepartmentResponse,
    EmployeeListItem,
    LeaveBalances
)

router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("", response_model=EmployeeListResponse)
def get_employees(
    search: Optional[str] = Query(None, description="Search by name, ID, or email"),
    department: Optional[int] = Query(None, description="Filter by department ID"),

    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Get paginated list of employees with dashboard stats"""
    
    employees, total_employees, department_count, new_joiners = EmployeeService.get_employees_with_stats(
        db=db,
        search=search,
        department_id=department,
        page=page,
        size=size
    )
    
    # Transform to response format
    employee_items = []
    for emp in employees:
        department_name = EmployeeService.get_department_name_by_id(db, emp.department_id)
        full_name = getattr(emp, 'full_name', None) or f"{emp.first_name} {emp.last_name}"
        employee_items.append(EmployeeListItem(
            employee_id=emp.employee_id,
            full_name=full_name,
            email_id=emp.email_id,
            department=department_name,
            designation=emp.designation,
            reporting_manager=emp.reporting_manager,
            joining_date=emp.joining_date,
            profile_photo=emp.profile_photo
        ))
    
    return EmployeeListResponse(
        total_employees=total_employees,
        department_count=department_count,
        new_joiners=new_joiners,
        employees=employee_items,
        page=page,
        size=size
    )

@router.get("/{employee_id}", response_model=EmployeeDetailResponse)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed employee information"""
    
    employee = EmployeeService.get_employee_by_id(db=db, employee_id=employee_id)
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Calculate monthly estimate (annual_ctc / 12 if available)
    monthly_estimate = None
    annual_ctc = getattr(employee, 'annual_ctc', None)
    if annual_ctc:
        monthly_estimate = int(annual_ctc / 12)
    
    # Calculate leave balances
    leave_balances = EmployeeService.calculate_leave_balances(db, employee_id, employee.annual_leaves)
    
    # Get department name
    department_name = EmployeeService.get_department_name_by_id(db, employee.department_id)
    
    # Build response with only requested fields
    full_name = getattr(employee, 'full_name', None) or f"{employee.first_name} {employee.last_name}"
    response_data = {
        "employee_id": employee.employee_id,
        "full_name": full_name,
        "designation": employee.designation,
        "status": getattr(employee, 'active_status', None) or "Active",
        "department": department_name,
        "email_id": employee.email_id,
        "phone_number": employee.phone_number,
        "reporting_manager": employee.reporting_manager,
        "joining_date": employee.joining_date,
        "employee_type": employee.employee_type,
        "annual_ctc": annual_ctc,
        "monthly_estimate": monthly_estimate,
        "casual_leave": leave_balances['casual_leave'],
        "sick_leave": leave_balances['sick_leave'],
        "earned_leave": leave_balances['earned_leave']
    }
    
    return EmployeeDetailResponse(**response_data)

@router.put("/{employee_id}", response_model=EmployeeUpdateResponse)
def update_employee(
    employee_id: str,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_hr_role)
):
    """Update employee details (HR Manager/Executive only)"""
    
    try:
        # Check if employee exists
        existing_employee = EmployeeService.get_employee_by_id(db=db, employee_id=employee_id)
        if not existing_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Validate email uniqueness if email is being updated
        if employee_update.email_id:
            if EmployeeService.check_email_exists(
                db=db, 
                email=employee_update.email_id, 
                exclude_employee_id=employee_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Email already exists for another employee"
                )
        
        # Validate department exists if department_name is being updated
        department_id = None
        if employee_update.department_name is not None:
            department_id = EmployeeService.get_department_id_by_name(db=db, department_name=employee_update.department_name)
            if not department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid department_name. Department does not exist."
                )
        
        # Validate reporting manager is not empty if being updated
        if employee_update.reporting_manager is not None:
            if employee_update.reporting_manager.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reporting manager cannot be empty."
                )
        
        # Update employee
        updated_employee = EmployeeService.update_employee(
            db=db,
            employee_id=employee_id,
            employee_update=employee_update,
            department_id=department_id
        )
        
        if not updated_employee:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update employee"
            )
        
        # Calculate leave balances
        leave_balances = EmployeeService.calculate_leave_balances(db, employee_id, updated_employee.annual_leaves)
        
        # Get department name
        department_name = EmployeeService.get_department_name_by_id(db, updated_employee.department_id)
        
        # Return updated employee with all current data (editable + read-only)
        full_name = getattr(updated_employee, 'full_name', None) or f"{updated_employee.first_name} {updated_employee.last_name}"
        annual_ctc = getattr(updated_employee, 'annual_ctc', None)
        return EmployeeUpdateResponse(
            employee_id=updated_employee.employee_id,
            full_name=full_name,
            email_id=updated_employee.email_id,
            status=getattr(updated_employee, 'active_status', None) or "Active",
            department=department_name,
            designation=updated_employee.designation,
            reporting_manager=updated_employee.reporting_manager,
            joining_date=updated_employee.joining_date,
            annual_ctc=annual_ctc,
            casual_leave=leave_balances['casual_leave'],
            sick_leave=leave_balances['sick_leave'],
            earned_leave=leave_balances['earned_leave']
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return a generic 500 error
        print(f"Unexpected error in update_employee: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the employee"
        )