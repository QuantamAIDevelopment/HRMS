from sqlalchemy.orm import Session
from src.models.salary import PayrollSetup
from src.models.hrms_models import Employee

from schemas.salary import SalaryCreate, PayrollSetupUpdate, SalaryComponentUpdate, ComponentDelete
from typing import Optional
from decimal import Decimal
from fastapi import HTTPException

class SalaryService:
    # Fixed values that cannot be changed
    FIXED_FIELDS = ['basic_salary', 'hra', 'allowance', 'professional_tax']
    
    @staticmethod
    def calculate_component_amount(annual_ctc: Decimal, component_amount: float, component_type: str, is_monthly: bool = True) -> Decimal:
        """Calculate component amount based on type (percentage or fixed)"""
        if component_type.lower() == "percentage":
            # Calculate percentage of annual CTC
            calculated = annual_ctc * Decimal(str(component_amount)) / 100
            return calculated / 12 if is_monthly else calculated
        else:
            # Fixed amount - return as is
            return Decimal(str(component_amount))
    
    @staticmethod
    def recalculate_payroll_totals(payroll_record: PayrollSetup, annual_ctc: Decimal, db: Session):
        """Recalculate payroll totals based on current components"""
        # Base earnings (always fixed monthly amounts)
        base_earnings = payroll_record.basic_salary + payroll_record.hra + payroll_record.allowance
        
        # Base deductions (PF percentage + fixed PT)
        pf_amount = (annual_ctc * payroll_record.provident_fund_percentage / 100) / 12
        base_deductions = pf_amount + payroll_record.professional_tax
        
        # Additional components
        additional_earnings = Decimal('0')
        additional_deductions = Decimal('0')
        
        if payroll_record.salary_components:
            components = payroll_record.salary_components
            if isinstance(components, str):
                import json
                components = json.loads(components)
            
            # Calculate additional earnings
            for earning in components.get("earnings", []):
                if "original_percentage" in earning:
                    # Use original percentage for accurate calculation
                    additional_earnings += SalaryService.calculate_component_amount(
                        annual_ctc, earning["original_percentage"], "percentage"
                    )
                else:
                    # Use stored amount (assume it's already calculated correctly)
                    additional_earnings += Decimal(str(earning["amount"]))
            
            # Calculate additional deductions
            for deduction in components.get("deductions", []):
                if "original_percentage" in deduction:
                    # Use original percentage for accurate calculation
                    additional_deductions += SalaryService.calculate_component_amount(
                        annual_ctc, deduction["original_percentage"], "percentage"
                    )
                else:
                    # Use stored amount (assume it's already calculated correctly)
                    additional_deductions += Decimal(str(deduction["amount"]))
        
        # Update totals
        payroll_record.total_earnings = base_earnings + additional_earnings
        payroll_record.total_deductions = base_deductions + additional_deductions
        payroll_record.net_salary = payroll_record.total_earnings - payroll_record.total_deductions
        
        return {
            "base_earnings": float(base_earnings),
            "additional_earnings": float(additional_earnings),
            "base_deductions": float(base_deductions),
            "additional_deductions": float(additional_deductions),
            "total_earnings": float(payroll_record.total_earnings),
            "total_deductions": float(payroll_record.total_deductions),
            "net_salary": float(payroll_record.net_salary)
        }
    
    @staticmethod
    def validate_fixed_fields(existing_record: PayrollSetup, update_data: dict):
        """Validate that fixed fields are not being modified"""
        errors = []
        
        for field in SalaryService.FIXED_FIELDS:
            if field in update_data:
                existing_value = getattr(existing_record, field, None)
                new_value = update_data[field]
                
                if existing_value is not None and new_value != existing_value:
                    errors.append(f"{field} is a fixed value and cannot be modified")
        
        if errors:
            raise HTTPException(status_code=400, detail={
                "message": "Cannot modify fixed payroll fields",
                "errors": errors,
                "allowed_fields": ["provident_fund_percentage"]
            })
    
    @staticmethod
    def update_payroll_setup(db: Session, payroll_id: int, update_data: PayrollSetupUpdate):
        """Update payroll setup with validation for fixed fields"""
        existing_record = db.query(PayrollSetup).filter(PayrollSetup.payroll_id == payroll_id).first()
        if not existing_record:
            raise HTTPException(status_code=404, detail="Payroll record not found")
        
        # Only allow updating provident_fund_percentage
        if update_data.provident_fund_percentage is not None:
            existing_record.provident_fund_percentage = update_data.provident_fund_percentage
            
            # Recalculate totals using helper method
            employee = db.query(Employee).filter(Employee.employee_id == existing_record.employee_id).first()
            if employee:
                annual_ctc = Decimal(employee.annual_ctc)
                calculation_breakdown = SalaryService.recalculate_payroll_totals(existing_record, annual_ctc, db)
        
        db.commit()
        db.refresh(existing_record)
        
        return {
            "message": "Payroll setup updated successfully",
            "payroll_id": payroll_id,
            "updated_fields": ["provident_fund_percentage"] if update_data.provident_fund_percentage is not None else [],
            "new_provident_fund_percentage": float(existing_record.provident_fund_percentage),
            "calculation_breakdown": calculation_breakdown if update_data.provident_fund_percentage is not None else None,
            "final_totals": {
                "total_earnings": float(existing_record.total_earnings),
                "total_deductions": float(existing_record.total_deductions),
                "net_salary": float(existing_record.net_salary)
            }
        }
    @staticmethod
    def create_salary_structure_by_employee_id(db: Session, employee_id: str, month: str, pay_cycle: str = "Monthly"):
        # Get employee information
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Convert annual CTC to numeric for calculations
        try:
            annual_ctc = Decimal(employee.annual_ctc)
        except:
            raise HTTPException(status_code=400, detail="Invalid annual CTC value")
        
        # Calculate salary components (basic calculations)
        basic_salary = annual_ctc * Decimal('0.40')  # 40% of CTC
        hra = annual_ctc * Decimal('0.20')  # 20% of CTC
        allowance = annual_ctc * Decimal('0.15')  # 15% of CTC
        
        # Calculate deductions
        provident_fund = annual_ctc * Decimal('0.12')  # 12% PF
        professional_tax = Decimal('2400')  # Annual PT
        
        # Calculate totals
        total_earnings = basic_salary + hra + allowance
        total_deductions = provident_fund + professional_tax
        net_salary = total_earnings - total_deductions
        
        # Calculate based on pay_cycle
        if pay_cycle.upper() == "MONTHLY":
            divisor = 12
        elif pay_cycle.upper() == "WEEKLY":
            divisor = 52
        elif pay_cycle.upper() in ["BIWEEKLY", "BI-WEEKLY"]:
            divisor = 26
        else:
            divisor = 12  # Default to monthly
        
        # Clean up any duplicate records first
        existing_record = SalaryService.cleanup_duplicate_records(db, employee_id, month)
        
        if existing_record:
            # Update existing record
            existing_record.designation = employee.designation
            existing_record.pay_cycle = pay_cycle
            existing_record.basic_salary = basic_salary / divisor
            existing_record.hra = hra / divisor
            existing_record.allowance = allowance / divisor
            existing_record.total_earnings = total_earnings / divisor
            existing_record.total_deductions = total_deductions / divisor
            existing_record.net_salary = net_salary / divisor
            payroll_setup = existing_record
        else:
            # Create new record only if none exists
            payroll_setup = PayrollSetup(
                employee_id=employee_id,
                designation=employee.designation,
                pay_cycle=pay_cycle,
                basic_salary=basic_salary / divisor,
                hra=hra / divisor,
                allowance=allowance / divisor,
                provident_fund_percentage=Decimal('12.00'),
                professional_tax=professional_tax / divisor,
                total_earnings=total_earnings / divisor,
                total_deductions=total_deductions / divisor,
                net_salary=net_salary / divisor,
                organization_name="QAID SOFTWARE",
                month=month,
                basic_salary_type="Fixed",
                hra_type="Percentage",
                allowance_type="Fixed",
                provident_fund_type="Percentage",
                professional_tax_type="Fixed"
            )
            db.add(payroll_setup)
        
        db.commit()
        db.refresh(payroll_setup)
        
        # Create filtered response
        filtered_response = {
            "employee_info": {
                "employee_id": employee.employee_id,
                "name": f"{employee.first_name} {employee.last_name}",
                "email": employee.email_id,
                "designation": employee.designation,
                "annual_ctc": float(annual_ctc)
            },
            "salary_structure": {
                "payroll_id": payroll_setup.payroll_id,
                "basic_salary": float(payroll_setup.basic_salary),
                "hra": float(payroll_setup.hra),
                "allowance": float(payroll_setup.allowance),
                "provident_fund_percentage": float(payroll_setup.provident_fund_percentage),
                "professional_tax": float(payroll_setup.professional_tax),
                "total_earnings": float(payroll_setup.total_earnings),
                "total_deductions": float(payroll_setup.total_deductions),
                "net_salary": float(payroll_setup.net_salary),
                "month": payroll_setup.month,
                "basic_salary_type": payroll_setup.basic_salary_type,
                "hra_type": payroll_setup.hra_type,
                "allowance_type": payroll_setup.allowance_type,
                "provident_fund_type": payroll_setup.provident_fund_type,
                "professional_tax_type": payroll_setup.professional_tax_type
            },
            "calculation_month": month
        }
        
        return filtered_response
    
    @staticmethod
    def get_salary_by_employee(db: Session, employee_id: str):
        salary_record = db.query(PayrollSetup).filter(PayrollSetup.employee_id == employee_id).first()
        if salary_record and salary_record.salary_components:
            if isinstance(salary_record.salary_components, str):
                import json
                try:
                    salary_record.salary_components = json.loads(salary_record.salary_components)
                    db.commit()
                except:
                    salary_record.salary_components = {"earnings": [], "deductions": []}
                    db.commit()
        return salary_record
    
    @staticmethod
    def get_all_salaries(db: Session):
        payroll_records = db.query(PayrollSetup).join(Employee, PayrollSetup.employee_id == Employee.employee_id).all()
        
        filtered_records = []
        for record in payroll_records:
            employee = db.query(Employee).filter(Employee.employee_id == record.employee_id).first()
            if employee:
                filtered_records.append({
                    "employee_name": f"{employee.first_name} {employee.last_name}",
                    "employee_id": record.employee_id,
                    "email_id": employee.email_id,
                    "role": record.designation,
                    "month": record.month
                })
        
        return filtered_records
    
    @staticmethod
    def get_employee_payslip(db: Session, employee_id: str, month: str = None):
        print(f"=== PAYSLIP DEBUG START ===")
        print(f"Employee ID: {employee_id}")
        print(f"Month: {month}")
        try:
            print(f"DEBUG: Starting payslip retrieval for {employee_id}, month: {month}")
            
            # Get employee information
            employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
            print(f"DEBUG: Employee found: {employee is not None}")
            if not employee:
                raise HTTPException(status_code=404, detail="Employee not found")
            
            # Build query for payroll setup
            query = db.query(PayrollSetup).filter(PayrollSetup.employee_id == employee_id)
            if month:
                query = query.filter(PayrollSetup.month == month)
            
            payroll_record = query.first()
            print(f"DEBUG: Payroll record found: {payroll_record is not None}")
            if not payroll_record:
                raise HTTPException(status_code=404, detail="Payslip not found for the specified employee/month")
        except HTTPException:
            raise
        except Exception as e:
            print(f"ERROR in get_employee_payslip query: {str(e)}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Database error: {str(e)}")
        
        try:
            print(f"DEBUG: Creating payslip response")
            
            # Prepare payslip response
            payslip_data = {
                "employee_info": {
                    "employee_id": employee.employee_id,
                    "name": f"{getattr(employee, 'first_name', '')} {getattr(employee, 'last_name', '')}",
                    "email": getattr(employee, 'email_id', ''),
                    "designation": getattr(employee, 'designation', ''),
                    "department_id": employee.department_id,
                    "joining_date": employee.joining_date.isoformat() if hasattr(employee, 'joining_date') and employee.joining_date else None,
                    "annual_ctc": float(getattr(employee, 'annual_ctc', 0))
                },
                "payslip_details": {
                    "month": getattr(payroll_record, 'month', '') or "",
                    "pay_cycle": getattr(payroll_record, 'pay_cycle', '') or "Monthly",
                    "organization_name": getattr(payroll_record, 'organization_name', '') or "",
                    "basic_salary": float(payroll_record.basic_salary) if payroll_record.basic_salary else 0.0,
                    "hra": float(payroll_record.hra) if payroll_record.hra else 0.0,
                    "allowance": float(payroll_record.allowance) if payroll_record.allowance else 0.0,
                    "provident_fund_percentage": float(payroll_record.provident_fund_percentage) if payroll_record.provident_fund_percentage else 0.0,
                    "professional_tax": float(payroll_record.professional_tax) if payroll_record.professional_tax else 0.0,
                    "total_earnings": float(payroll_record.total_earnings) if payroll_record.total_earnings else 0.0,
                    "total_deductions": float(payroll_record.total_deductions) if payroll_record.total_deductions else 0.0,
                    "net_salary": float(payroll_record.net_salary) if payroll_record.net_salary else 0.0,
                    "salary_components": SalaryService._fix_salary_components(db, payroll_record) if payroll_record.salary_components else {"earnings": [], "deductions": []}
                },
                "generated_at": payroll_record.created_at.isoformat() if hasattr(payroll_record, 'created_at') and payroll_record.created_at else None
            }
            
            print(f"DEBUG: Payslip data created successfully")
            return payslip_data
        except Exception as e:
            print(f"ERROR creating payslip response: {str(e)}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error creating payslip response: {str(e)}")
    
    @staticmethod
    def _fix_salary_components(db: Session, payroll_record):
        try:
            print(f"DEBUG: Fixing salary components")
            if hasattr(payroll_record, 'salary_components') and payroll_record.salary_components:
                if isinstance(payroll_record.salary_components, str):
                    import json
                    try:
                        fixed_components = json.loads(payroll_record.salary_components)
                        payroll_record.salary_components = fixed_components
                        db.commit()
                        return fixed_components
                    except Exception as e:
                        print(f"ERROR parsing salary_components JSON: {str(e)}")
                        return {"earnings": [], "deductions": []}
                else:
                    return payroll_record.salary_components
            return {"earnings": [], "deductions": []}
        except Exception as e:
            print(f"ERROR in _fix_salary_components: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"earnings": [], "deductions": []}
    
    @staticmethod
    def save_salary_structure(db: Session, salary_data):
        # Get employee information
        employee = db.query(Employee).filter(Employee.employee_id == salary_data.employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Calculate base salary from annual CTC
        try:
            annual_ctc = Decimal(employee.annual_ctc)
        except:
            raise HTTPException(status_code=400, detail="Invalid annual CTC value")
        
        # Base calculations (monthly)
        basic_salary = annual_ctc * Decimal('0.40') / 12
        hra = annual_ctc * Decimal('0.20') / 12
        allowance = annual_ctc * Decimal('0.15') / 12
        
        # Calculate additional earnings with proper percentage handling
        total_additional_earnings = Decimal('0')
        earnings_list = []
        for earning in salary_data.earnings:
            if earning.component_type.lower() == "percentage":
                # Calculate percentage of annual CTC, then convert to monthly
                calculated_amount = (annual_ctc * Decimal(str(earning.amount)) / 100) / 12
                total_additional_earnings += calculated_amount
                earnings_list.append({
                    "component_name": earning.component_name,
                    "amount": float(calculated_amount),
                    "component_type": earning.component_type,
                    "original_percentage": float(earning.amount)
                })
            else:  # fixed amount
                fixed_amount = Decimal(str(earning.amount))
                total_additional_earnings += fixed_amount
                earnings_list.append({
                    "component_name": earning.component_name,
                    "amount": float(fixed_amount),
                    "component_type": earning.component_type
                })
        
        # Calculate deductions with proper percentage handling
        provident_fund = annual_ctc * Decimal('0.12') / 12
        professional_tax = Decimal('200')  # Monthly PT
        
        total_additional_deductions = Decimal('0')
        deductions_list = []
        for deduction in salary_data.deductions:
            if deduction.component_type.lower() == "percentage":
                # Calculate percentage of annual CTC, then convert to monthly
                calculated_amount = (annual_ctc * Decimal(str(deduction.amount)) / 100) / 12
                total_additional_deductions += calculated_amount
                deductions_list.append({
                    "component_name": deduction.component_name,
                    "amount": float(calculated_amount),
                    "component_type": deduction.component_type,
                    "original_percentage": float(deduction.amount)
                })
            else:  # fixed amount
                fixed_amount = Decimal(str(deduction.amount))
                total_additional_deductions += fixed_amount
                deductions_list.append({
                    "component_name": deduction.component_name,
                    "amount": float(fixed_amount),
                    "component_type": deduction.component_type
                })
        
        # Calculate final totals
        total_earnings = basic_salary + hra + allowance + total_additional_earnings
        total_deductions = provident_fund + professional_tax + total_additional_deductions
        net_salary = total_earnings - total_deductions
        
        # Store components as proper dict
        salary_components_json = {
            "earnings": earnings_list,
            "deductions": deductions_list
        }
        
        # Clean up duplicates and update/create record
        existing_record = SalaryService.cleanup_duplicate_records(db, salary_data.employee_id, salary_data.pay_month)
        
        if existing_record:
            # Update existing record with recalculated values
            existing_record.pay_cycle = salary_data.pay_cycle
            existing_record.basic_salary = basic_salary
            existing_record.hra = hra
            existing_record.allowance = allowance
            existing_record.total_earnings = total_earnings
            existing_record.total_deductions = total_deductions
            existing_record.net_salary = net_salary
            existing_record.salary_components = salary_components_json
            payroll_setup = existing_record
        else:
            # Create new record
            payroll_setup = PayrollSetup(
                employee_id=salary_data.employee_id,
                designation=employee.designation,
                pay_cycle=salary_data.pay_cycle,
                basic_salary=basic_salary,
                hra=hra,
                allowance=allowance,
                provident_fund_percentage=Decimal('12.00'),
                professional_tax=professional_tax,
                total_earnings=total_earnings,
                total_deductions=total_deductions,
                net_salary=net_salary,
                organization_name="QAID SOFTWARE",
                month=salary_data.pay_month,
                basic_salary_type="Fixed",
                hra_type="Percentage",
                allowance_type="Fixed",
                provident_fund_type="Percentage",
                professional_tax_type="Fixed",
                salary_components=salary_components_json
            )
            db.add(payroll_setup)
        
        db.commit()
        db.refresh(payroll_setup)
        
        return {
            "message": "Salary structure saved successfully",
            "payroll_id": payroll_setup.payroll_id,
            "employee_id": salary_data.employee_id,
            "pay_month": salary_data.pay_month,
            "annual_ctc": float(annual_ctc),
            "breakdown": {
                "basic_salary": float(basic_salary),
                "hra": float(hra),
                "allowance": float(allowance),
                "additional_earnings": float(total_additional_earnings),
                "provident_fund": float(provident_fund),
                "professional_tax": float(professional_tax),
                "additional_deductions": float(total_additional_deductions)
            },
            "total_earnings": float(total_earnings),
            "total_deductions": float(total_deductions),
            "net_salary": float(net_salary),
            "salary_components": salary_components_json
        }
    
    @staticmethod
    def get_salary_summary(db: Session, employee_id: str):
        # Employee already imported at top
        from datetime import datetime
        
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        payroll_records = db.query(PayrollSetup).filter(PayrollSetup.employee_id == employee_id).all()
        
        if not payroll_records:
            raise HTTPException(status_code=404, detail="No payroll records found")
        
        try:
            annual_ctc = float(employee.annual_ctc)
        except:
            annual_ctc = 0.0
        
        latest_record = max(payroll_records, key=lambda x: x.created_at)
        current_net_pay = float(latest_record.net_salary) if latest_record.net_salary else 0.0
        
        joining_date = employee.joining_date
        current_date = datetime.now().date()
        
        if current_date.month >= 4:
            fy_start = datetime(current_date.year, 4, 1).date()
        else:
            fy_start = datetime(current_date.year - 1, 4, 1).date()
        
        ytd_start_date = max(joining_date, fy_start)
        
        ytd_total = 0.0
        months_worked = 0
        
        for record in payroll_records:
            if record.created_at and record.created_at.date() >= ytd_start_date:
                if record.net_salary:
                    ytd_total += float(record.net_salary)
                    months_worked += 1
        
        return {
            "annual_ctc": annual_ctc,
            "current_month_net_pay": current_net_pay,
            "ytd_total": ytd_total
        }
    
    @staticmethod
    def update_salary_components(db: Session, update_data: SalaryComponentUpdate):
        """Edit components and recalculate totals"""
        from sqlalchemy.orm.attributes import flag_modified
        
        try:
            payroll_record = db.query(PayrollSetup).filter(
                PayrollSetup.employee_id == update_data.employee_id,
                PayrollSetup.month == update_data.month
            ).first()
            
            if not payroll_record:
                return {"error": "Payroll record not found"}
            
            # Get employee for CTC
            employee = db.query(Employee).filter(Employee.employee_id == update_data.employee_id).first()
            if not employee:
                return {"error": "Employee not found"}
            
            annual_ctc = Decimal(employee.annual_ctc)
            
            # Process earnings with calculations
            earnings_list = []
            additional_earnings = Decimal('0')
            for earning in update_data.earnings:
                if earning.component_type.lower() == "percentage":
                    amount = (annual_ctc * Decimal(str(earning.amount)) / 100) / 12
                    earnings_list.append({
                        "component_name": earning.component_name,
                        "amount": float(amount),
                        "component_type": earning.component_type,
                        "original_percentage": float(earning.amount)
                    })
                else:
                    amount = Decimal(str(earning.amount))
                    earnings_list.append({
                        "component_name": earning.component_name,
                        "amount": float(amount),
                        "component_type": earning.component_type
                    })
                additional_earnings += amount
            
            # Process deductions with calculations
            deductions_list = []
            additional_deductions = Decimal('0')
            for deduction in update_data.deductions:
                if deduction.component_type.lower() == "percentage":
                    amount = (annual_ctc * Decimal(str(deduction.amount)) / 100) / 12
                    deductions_list.append({
                        "component_name": deduction.component_name,
                        "amount": float(amount),
                        "component_type": deduction.component_type,
                        "original_percentage": float(deduction.amount)
                    })
                else:
                    amount = Decimal(str(deduction.amount))
                    deductions_list.append({
                        "component_name": deduction.component_name,
                        "amount": float(amount),
                        "component_type": deduction.component_type
                    })
                additional_deductions += amount
            
            # Update components and recalculate totals
            components = {"earnings": earnings_list, "deductions": deductions_list}
            
            base_earnings = payroll_record.basic_salary + payroll_record.hra + payroll_record.allowance
            base_deductions = (annual_ctc * payroll_record.provident_fund_percentage / 100) / 12 + payroll_record.professional_tax
            
            payroll_record.salary_components = components
            flag_modified(payroll_record, "salary_components")
            payroll_record.total_earnings = base_earnings + additional_earnings
            payroll_record.total_deductions = base_deductions + additional_deductions
            payroll_record.net_salary = payroll_record.total_earnings - payroll_record.total_deductions
            
            db.commit()
            db.refresh(payroll_record)
            
            return {
                "message": "Components updated and payslip recalculated",
                "payroll_id": payroll_record.payroll_id,
                "employee_id": update_data.employee_id,
                "month": update_data.month,
                "new_totals": {
                    "total_earnings": float(payroll_record.total_earnings),
                    "total_deductions": float(payroll_record.total_deductions),
                    "net_salary": float(payroll_record.net_salary)
                },
                "updated_components": components
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_salary_history(db: Session, employee_id: str):
        """Get salary history for employee"""
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get unique records by employee_id (should be one per month now)
        payroll_records = db.query(PayrollSetup).filter(
            PayrollSetup.employee_id == employee_id
        ).order_by(PayrollSetup.created_at.desc()).all()
        
        if not payroll_records:
            raise HTTPException(status_code=404, detail="No salary records found")
        
        salary_history = []
        for record in payroll_records:
            # Extract year from month if format is "Month Year" or use current year
            month_parts = record.month.split()
            if len(month_parts) == 2:
                month, year = month_parts[0], month_parts[1]
            else:
                month = record.month
                year = str(record.created_at.year) if record.created_at else "2024"
            
            salary_history.append({
                "month": month,
                "year": year,
                "basic_salary": float(record.basic_salary) if record.basic_salary else 0.0,
                "allowances": float(record.hra + record.allowance) if record.hra and record.allowance else 0.0,
                "deductions": float(record.total_deductions) if record.total_deductions else 0.0,
                "net_pay": float(record.net_salary) if record.net_salary else 0.0
            })
        
        # Sort by month order
        month_order = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
                      "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}
        
        salary_history.sort(key=lambda x: month_order.get(x["month"].lower(), 13), reverse=True)
        
        return {
            "employee_id": employee_id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "salary_history": salary_history
        }
    
    @staticmethod
    def delete_salary_component(db: Session, delete_data: ComponentDelete):
        """Delete component and recalculate totals"""
        print(f"DELETE DEBUG: employee_id={delete_data.employee_id}, month={delete_data.month}, component={delete_data.component_name}, type={delete_data.component_type}")
        try:
            payroll_record = db.query(PayrollSetup).filter(
                PayrollSetup.employee_id == delete_data.employee_id,
                PayrollSetup.month == delete_data.month
            ).first()
            
            if not payroll_record:
                raise HTTPException(status_code=404, detail="Payroll record not found")
            
            # Get employee for CTC
            employee = db.query(Employee).filter(Employee.employee_id == delete_data.employee_id).first()
            if not employee:
                raise HTTPException(status_code=404, detail="Employee not found")
            
            annual_ctc = Decimal(employee.annual_ctc)
            
            # Get components
            components = payroll_record.salary_components or {"earnings": [], "deductions": []}
            if isinstance(components, str):
                import json
                components = json.loads(components)
            
            # Remove component (case-insensitive and strip whitespace)
            component_to_delete = delete_data.component_name.strip().lower()
            deleted = False
            
            if delete_data.component_type.lower() == "earnings":
                original_count = len(components.get("earnings", []))
                components["earnings"] = [c for c in components.get("earnings", []) 
                                        if c["component_name"].strip().lower() != component_to_delete]
                deleted = len(components["earnings"]) < original_count
            else:
                original_count = len(components.get("deductions", []))
                components["deductions"] = [c for c in components.get("deductions", []) 
                                          if c["component_name"].strip().lower() != component_to_delete]
                deleted = len(components["deductions"]) < original_count
            
            if not deleted:
                raise HTTPException(status_code=404, detail=f"Component '{delete_data.component_name}' not found")
            
            # Recalculate additional amounts
            additional_earnings = Decimal('0')
            for earning in components.get("earnings", []):
                if earning["component_type"].lower() == "percentage":
                    additional_earnings += (annual_ctc * Decimal(str(earning.get("original_percentage", earning["amount"]))) / 100) / 12
                else:
                    additional_earnings += Decimal(str(earning["amount"]))
            
            additional_deductions = Decimal('0')
            for deduction in components.get("deductions", []):
                if deduction["component_type"].lower() == "percentage":
                    additional_deductions += (annual_ctc * Decimal(str(deduction.get("original_percentage", deduction["amount"]))) / 100) / 12
                else:
                    additional_deductions += Decimal(str(deduction["amount"]))
            
            # Update totals
            base_earnings = payroll_record.basic_salary + payroll_record.hra + payroll_record.allowance
            base_deductions = (annual_ctc * payroll_record.provident_fund_percentage / 100) / 12 + payroll_record.professional_tax
            
            payroll_record.salary_components = components
            payroll_record.total_earnings = base_earnings + additional_earnings
            payroll_record.total_deductions = base_deductions + additional_deductions
            payroll_record.net_salary = payroll_record.total_earnings - payroll_record.total_deductions
            
            db.commit()
            db.refresh(payroll_record)
            
            return {
                "message": "Component deleted and payslip recalculated",
                "payroll_id": payroll_record.payroll_id,
                "employee_id": delete_data.employee_id,
                "month": delete_data.month,
                "deleted_component": delete_data.component_name,
                "new_totals": {
                    "total_earnings": float(payroll_record.total_earnings),
                    "total_deductions": float(payroll_record.total_deductions),
                    "net_salary": float(payroll_record.net_salary)
                },
                "remaining_components": components
            }
        except HTTPException:
            raise
        except Exception as e:
            error_msg = str(e) if str(e).strip() else f"Unknown error of type {type(e).__name__}"
            print(f"DELETE COMPONENT ERROR: {error_msg}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting component: {error_msg}")
    
    @staticmethod
    def cleanup_duplicate_records(db: Session, employee_id: str, month: str):
        """Remove duplicate records, keep only the latest one"""
        duplicate_records = db.query(PayrollSetup).filter(
            PayrollSetup.employee_id == employee_id,
            PayrollSetup.month == month
        ).order_by(PayrollSetup.created_at.desc()).all()
        
        if len(duplicate_records) > 1:
            # Keep the first (latest) record, delete the rest
            latest_record = duplicate_records[0]
            for record in duplicate_records[1:]:
                db.delete(record)
            db.commit()
            return latest_record
        elif len(duplicate_records) == 1:
            return duplicate_records[0]
        return None
    
    @staticmethod
    def delete_payslip(db: Session, employee_id: str, month: str):
        """Delete payslip by employee_id and month"""
        payroll_record = db.query(PayrollSetup).filter(
            PayrollSetup.employee_id == employee_id,
            PayrollSetup.month == month
        ).first()
        
        if not payroll_record:
            raise HTTPException(status_code=404, detail="Payslip not found")
        
        payroll_id = payroll_record.payroll_id
        db.delete(payroll_record)
        db.commit()
        
        return {
            "message": "Payslip deleted successfully",
            "payroll_id": payroll_id,
            "employee_id": employee_id,
            "month": month
        }
    
    @staticmethod
    def check_components(db: Session, employee_id: str, month: str):
        """Check salary components for employee and month"""
        payroll_record = db.query(PayrollSetup).filter(
            PayrollSetup.employee_id == employee_id,
            PayrollSetup.month == month
        ).first()
        
        if not payroll_record:
            all_records = db.query(PayrollSetup).filter(PayrollSetup.employee_id == employee_id).all()
            available_months = [r.month for r in all_records]
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": "Payroll record not found",
                    "employee_id": employee_id,
                    "requested_month": month,
                    "available_months": available_months
                }
            )
        
        components = payroll_record.salary_components or {"earnings": [], "deductions": []}
        if isinstance(components, str):
            import json
            components = json.loads(components)
        
        return {
            "employee_id": employee_id,
            "month": month,
            "payroll_id": payroll_record.payroll_id,
            "components": components
        }
    
    @staticmethod
    def force_delete_component(db: Session, employee_id: str, month: str, component_name: str):
        """Force delete a specific salary component"""
        from sqlalchemy.orm.attributes import flag_modified
        
        payroll_record = db.query(PayrollSetup).filter(
            PayrollSetup.employee_id == employee_id,
            PayrollSetup.month == month
        ).first()
        
        if not payroll_record:
            raise HTTPException(status_code=404, detail="Payroll record not found")
        
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        annual_ctc = Decimal(employee.annual_ctc)
        
        components = payroll_record.salary_components or {"earnings": [], "deductions": []}
        if isinstance(components, str):
            import json
            components = json.loads(components)
        
        component_lower = component_name.strip().lower()
        deleted = False
        
        original_earnings = len(components.get("earnings", []))
        components["earnings"] = [c for c in components.get("earnings", []) 
                                if c["component_name"].strip().lower() != component_lower]
        if len(components["earnings"]) < original_earnings:
            deleted = True
        
        if not deleted:
            original_deductions = len(components.get("deductions", []))
            components["deductions"] = [c for c in components.get("deductions", []) 
                                      if c["component_name"].strip().lower() != component_lower]
            if len(components["deductions"]) < original_deductions:
                deleted = True
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
        
        # Recalculate totals
        additional_earnings = Decimal('0')
        for earning in components.get("earnings", []):
            if earning["component_type"].lower() == "percentage":
                additional_earnings += (annual_ctc * Decimal(str(earning.get("original_percentage", earning["amount"]))) / 100) / 12
            else:
                additional_earnings += Decimal(str(earning["amount"]))
        
        additional_deductions = Decimal('0')
        for deduction in components.get("deductions", []):
            if deduction["component_type"].lower() == "percentage":
                additional_deductions += (annual_ctc * Decimal(str(deduction.get("original_percentage", deduction["amount"]))) / 100) / 12
            else:
                additional_deductions += Decimal(str(deduction["amount"]))
        
        base_earnings = payroll_record.basic_salary + payroll_record.hra + payroll_record.allowance
        base_deductions = (annual_ctc * payroll_record.provident_fund_percentage / 100) / 12 + payroll_record.professional_tax
        
        payroll_record.salary_components = components
        flag_modified(payroll_record, "salary_components")
        payroll_record.total_earnings = base_earnings + additional_earnings
        payroll_record.total_deductions = base_deductions + additional_deductions
        payroll_record.net_salary = payroll_record.total_earnings - payroll_record.total_deductions
        
        db.commit()
        db.refresh(payroll_record)
        
        return {
            "message": "Component deleted successfully",
            "employee_id": employee_id,
            "month": month,
            "deleted_component": component_name,
            "new_totals": {
                "total_earnings": float(payroll_record.total_earnings),
                "total_deductions": float(payroll_record.total_deductions),
                "net_salary": float(payroll_record.net_salary)
            },
            "remaining_components": components
        }
    
