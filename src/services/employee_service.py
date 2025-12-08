from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import Optional, Tuple, List
from datetime import date, timedelta
from ..models.hrms_models import Employee, Department, LeaveManagement
from ..schemas.employee import EmployeeUpdate

class EmployeeService:
    
    @staticmethod
    def get_employees_with_stats(
        db: Session,
        search: Optional[str] = None,
        department_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Employee], int, int, int]:
        """Get paginated employees with dashboard stats"""
        
        # Base query
        query = db.query(Employee)
        
        # Apply filters
        if search:
            search_filter = or_(
                Employee.first_name.ilike(f"%{search}%"),
                Employee.last_name.ilike(f"%{search}%"),
                Employee.employee_id.ilike(f"%{search}%"),
                Employee.email_id.ilike(f"%{search}%"),
                Employee.full_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        # Get filtered count for pagination
        filtered_count = query.count()
        
        # Get total employees count (all employees in DB)
        total_employees = db.query(Employee).count()
        
        # Get paginated results  
        employees = query.order_by(Employee.first_name)\
                         .offset((page - 1) * size)\
                         .limit(size)\
                         .all()
        
        # Calculate dashboard stats
        department_count = db.query(Department).count()
        
        # New joiners (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        new_joiners = db.query(Employee)\
                       .filter(Employee.joining_date >= thirty_days_ago)\
                       .count()
        
        return employees, total_employees, department_count, new_joiners
    
    @staticmethod
    def get_employee_by_id(db: Session, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        return db.query(Employee)\
                 .filter(Employee.employee_id == employee_id)\
                 .first()
    
    @staticmethod
    def get_department_by_id(db: Session, department_id: int) -> Optional[Department]:
        """Get department by ID"""
        return db.query(Department)\
                 .filter(Department.department_id == department_id)\
                 .first()
    
    @staticmethod
    def get_department_name_by_id(db: Session, department_id: int) -> str:
        """Get department name by ID"""
        dept = db.query(Department)\
                 .filter(Department.department_id == department_id)\
                 .first()
        return dept.department_name if dept else "Unknown"
    
    @staticmethod
    def get_department_id_by_name(db: Session, department_name: str) -> Optional[int]:
        """Get department ID by name"""
        dept = db.query(Department)\
                 .filter(Department.department_name.ilike(department_name.strip()))\
                 .first()
        return dept.department_id if dept else None
    
    @staticmethod
    def update_employee(
        db: Session, 
        employee_id: str, 
        employee_update: EmployeeUpdate,
        department_id: Optional[int] = None
    ) -> Optional[Employee]:
        """Update employee details"""
        try:
            employee = db.query(Employee)\
                        .filter(Employee.employee_id == employee_id)\
                        .first()
            
            if not employee:
                return None
            
            # Update fields (exclude full_name as it's generated)
            update_data = employee_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field != 'full_name' and hasattr(employee, field):
                    # Skip None values but allow empty strings and 0 values if they're valid
                    if value is None:
                        continue
                    
                    # Skip department_name as it's handled separately
                    if field == 'department_name':
                        continue
                    
                    # Map status field to active_status column
                    if field == 'status':
                        setattr(employee, 'active_status', value)
                        continue
                    
                    # Set the field value
                    setattr(employee, field, value)
            
            # Handle department_id separately if provided
            if department_id is not None:
                setattr(employee, 'department_id', department_id)
            
            db.commit()
            db.refresh(employee)
            return employee
            
        except Exception as e:
            db.rollback()
            print(f"Error updating employee {employee_id}: {e}")
            return None
    
    @staticmethod
    def check_email_exists(db: Session, email: str, exclude_employee_id: Optional[str] = None) -> bool:
        """Check if email already exists for another employee"""
        query = db.query(Employee).filter(Employee.email_id == email)
        if exclude_employee_id:
            query = query.filter(Employee.employee_id != exclude_employee_id)
        return query.first() is not None
    
    @staticmethod
    def check_department_exists(db: Session, department_id: int) -> bool:
        """Check if department exists"""
        return db.query(Department).filter(Department.department_id == department_id).first() is not None
    
    @staticmethod
    def get_all_departments(db: Session) -> List[Department]:
        """Get all departments for dropdown"""
        return db.query(Department).order_by(Department.department_name).all()
    
    @staticmethod
    def check_employee_exists(db: Session, employee_id: str) -> bool:
        """Check if employee exists"""
        return db.query(Employee).filter(Employee.employee_id == employee_id).first() is not None
    
    @staticmethod
    def calculate_leave_balances(db: Session, employee_id: str, annual_leaves: int):
        """Calculate leave balances based on annual_leaves and used leaves from leave_management"""
        # Get approved leaves from leave_management table
        used_casual = db.query(func.coalesce(func.sum(LeaveManagement.employee_used_leaves), 0))\
                       .filter(LeaveManagement.employee_id == employee_id,
                              LeaveManagement.leave_type.ilike('%casual%'),
                              LeaveManagement.status == 'Approved').scalar() or 0
        
        used_sick = db.query(func.coalesce(func.sum(LeaveManagement.employee_used_leaves), 0))\
                     .filter(LeaveManagement.employee_id == employee_id,
                            LeaveManagement.leave_type.ilike('%sick%'),
                            LeaveManagement.status == 'Approved').scalar() or 0
        
        used_earned = db.query(func.coalesce(func.sum(LeaveManagement.employee_used_leaves), 0))\
                       .filter(LeaveManagement.employee_id == employee_id,
                              LeaveManagement.leave_type.ilike('%earned%'),
                              LeaveManagement.status == 'Approved').scalar() or 0
        
        # Divide annual_leaves among leave types
        total_annual = annual_leaves or 21
        casual_allocation = total_annual // 3
        sick_allocation = total_annual // 3
        earned_allocation = total_annual - casual_allocation - sick_allocation
        
        # Calculate remaining balances
        casual_balance = max(0, casual_allocation - used_casual)
        sick_balance = max(0, sick_allocation - used_sick)
        earned_balance = max(0, earned_allocation - used_earned)
        
        return {
            'casual_leave': casual_balance,
            'sick_leave': sick_balance,
            'earned_leave': earned_balance
        }