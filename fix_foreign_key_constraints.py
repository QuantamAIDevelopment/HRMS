# Foreign Key Constraint Fixes for Employee Onboarding

def validate_foreign_keys_before_creation(db, department_name, shift_name, asset_requests):
    """Validate all foreign key dependencies before creating employee"""
    from models.Employee_models import Department, ShiftMaster, Assets
    
    # 1. Validate/Create Department
    department = db.query(Department).filter(Department.department_name == department_name).first()
    if not department:
        department = Department(department_name=department_name)
        db.add(department)
        db.flush()  # Ensure department_id is available
    
    # 2. Validate/Create Shift
    shift = db.query(ShiftMaster).filter(ShiftMaster.shift_name == shift_name).first()
    if not shift:
        from datetime import datetime
        shift = ShiftMaster(
            shift_name=shift_name,
            shift_type="Regular",
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("18:00", "%H:%M").time()
        )
        db.add(shift)
        db.flush()
    
    # 3. Validate Assets Availability
    for asset_req in asset_requests:
        asset = db.query(Assets).filter(
            Assets.serial_number == asset_req.get("serial_number"),
            Assets.asset_type == asset_req.get("asset_type"),
            Assets.status == "Available"
        ).first()
        
        if not asset:
            raise ValueError(f"Asset {asset_req.get('serial_number')} not available")
    
    return department, shift

def create_employee_with_proper_fk_handling(db, employee_data, personal_data, bank_data, 
                                          education_list, work_exp_list, doc_list, asset_list):
    """Create employee with proper foreign key constraint handling"""
    from models.Employee_models import Employee, BankDetails, EducationalQualifications, EmployeeDocuments, Assets
    from models.Employee_models import EmployeePersonalDetails as EmpPersonalDetails
    from models.user import User
    from core.security import get_password_hash
    
    try:
        # Step 1: Validate all foreign keys first
        department, shift = validate_foreign_keys_before_creation(
            db, employee_data['department_name'], 
            employee_data.get('shift_name', 'General Shift'), 
            asset_list
        )
        
        # Step 2: Create Employee (parent record)
        employee = Employee(
            employee_id=employee_data['employee_id'],
            first_name=employee_data['first_name'],
            last_name=employee_data['last_name'],
            department_id=department.department_id,  # Use validated department_id
            shift_id=shift.shift_id,  # Use validated shift_id
            **{k: v for k, v in employee_data.items() 
               if k not in ['department_name', 'shift_name']}
        )
        db.add(employee)
        db.flush()  # Ensure employee_id is available for foreign keys
        
        # Step 3: Create dependent records with proper employee_id
        if personal_data:
            personal_data['employee_id'] = employee.employee_id
            personal_details = EmpPersonalDetails(**personal_data)
            db.add(personal_details)
        
        if bank_data:
            bank_data['employee_id'] = employee.employee_id
            bank_details = BankDetails(**bank_data)
            db.add(bank_details)
        
        # Step 4: Create array records
        for edu in education_list:
            edu['employee_id'] = employee.employee_id
            education = EducationalQualifications(**edu)
            db.add(education)
        
        for exp in work_exp_list:
            exp['employee_id'] = employee.employee_id
            work_exp = EmployeeWorkExperience(**exp)
            db.add(work_exp)
        
        for doc in doc_list:
            doc['employee_id'] = employee.employee_id
            document = EmployeeDocuments(**doc)
            db.add(document)
        
        # Step 5: Assign assets with proper validation
        for asset_req in asset_list:
            asset = db.query(Assets).filter(
                Assets.serial_number == asset_req.get("serial_number"),
                Assets.asset_type == asset_req.get("asset_type"),
                Assets.status == "Available"
            ).first()
            
            if asset:
                asset.employee_id = employee.employee_id
                asset.status = "Assigned"
        
        # Step 6: Create User record last
        user = User(
            employee_id=employee.employee_id,  # Use flushed employee_id
            email=employee_data['email_id'],
            hashed_password=get_password_hash("TempPass123!"),
            full_name=f"{employee.first_name} {employee.last_name}",
            role="EMPLOYEE"
        )
        db.add(user)
        
        # Step 7: Commit all changes together
        db.commit()
        return employee.employee_id
        
    except Exception as e:
        db.rollback()
        raise e