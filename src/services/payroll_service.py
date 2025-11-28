from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.payroll import Payroll
from src.models.payroll_setup import PayrollSetup
from src.schemas.payroll_schemas import PayrollCreate
from src.schemas.payroll_setup import PayrollSetupCreate
from src.schemas.salary_structure import SalaryStructureRequest, SalaryStructureResponse, SalaryStructureData, EarningsStructure, DeductionsStructure
from src.schemas.component_request import ComponentRequest

class PayrollService:
    @staticmethod
    def create_salary_structure(db: Session, request: SalaryStructureRequest):
        from src.models.onboarding_process import OnboardingProcess
        
        # Get employee details from onboarding_process table
        employee = db.query(OnboardingProcess).filter(
            OnboardingProcess.employee_id == request.employee_id
        ).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        annual_ctc = float(employee.annual_ctc)
        
        # Calculate salary components
        basic_salary = annual_ctc * 0.4 / 12  # 40% of CTC as basic salary
        hra = annual_ctc * 0.2 / 12           # 20% as HRA
        allowance = annual_ctc * 0.4 / 12     # 40% as allowances
        
        # Calculate deductions
        provident_fund = basic_salary * 0.12  # 12% of basic salary
        professional_tax = 200                # Fixed professional tax
        
        total_earnings = basic_salary + hra + allowance
        total_deductions = provident_fund + professional_tax
        net_salary = total_earnings - total_deductions
        
        # Create salary structure response
        earnings = EarningsStructure(
            basic_salary=basic_salary,
            basic_salary_type="Fixed",
            hra=hra,
            hra_type="Fixed",
            allowance=allowance,
            allowance_type="Fixed"
        )
        
        deductions = DeductionsStructure(
            provident_fund=provident_fund,
            provident_fund_type="Percentage",
            professional_tax=professional_tax,
            professional_tax_type="Fixed"
        )
        
        salary_structure = SalaryStructureData(
            earnings=earnings,
            deductions=deductions
        )
        
        # Store in payroll_setup table
        payroll_setup = PayrollSetup(
            employee_id=request.employee_id,
            pay_cycle=request.pay_cycle_type,
            month=request.month,
            basic_salary=basic_salary,
            hra=hra,
            allowance=allowance,
            provident_fund_percentage=12.0,
            professional_tax=professional_tax,
            total_earnings=total_earnings,
            total_deductions=total_deductions,
            net_salary=net_salary
        )
        
        db.add(payroll_setup)
        db.commit()
        
        return SalaryStructureResponse(
            salary_structure=salary_structure,
            annual_ctc=annual_ctc,
            total_earnings=total_earnings,
            total_deductions=total_deductions,
            net_salary=net_salary
        )
    
    @staticmethod
    def create_payroll(db: Session, payroll: PayrollCreate):
        db_payroll = Payroll(
            employee_id=payroll.employee_id,
            pay_period_start=payroll.pay_period_start,
            pay_period_end=payroll.pay_period_end,
            basic_salary=payroll.basic_salary,
            allowances=payroll.allowances,
            deductions=payroll.deductions,
            overtime_hours=payroll.overtime_hours,
            overtime_amount=payroll.overtime_amount,
            gross_pay=payroll.gross_pay,
            tax_amount=payroll.tax_amount,
            net_pay=payroll.net_pay
        )
        db.add(db_payroll)
        db.commit()
        db.refresh(db_payroll)
        return db_payroll
    
    @staticmethod
    def get_all_payroll(db: Session):
        return db.query(Payroll).all()
    
    @staticmethod
    def get_payroll_by_id(db: Session, payroll_id: int):
        return db.query(Payroll).filter(Payroll.payroll_id == payroll_id).first()
    
    @staticmethod
    def create_payroll_setup(db: Session, setup: PayrollSetupCreate):
        db_setup = PayrollSetup(
            employee_id=setup.employee_id,
            basic_salary=setup.basic_salary,
            allowances=setup.allowances,
            deductions=setup.deductions,
            tax_rate=setup.tax_rate,
            overtime_rate=setup.overtime_rate,
            is_active=setup.is_active
        )
        db.add(db_setup)
        db.commit()
        db.refresh(db_setup)
        return db_setup
    
    @staticmethod
    def get_all_payroll_setup(db: Session):
        return db.query(PayrollSetup).all()
    
    @staticmethod
    def add_earnings_component(db: Session, employee_id: str, request: ComponentRequest):
        from src.models.onboarding_process import OnboardingProcess
        
        # Add earnings component to payroll setup
        setup = PayrollSetup(
            employee_id=employee_id,
            component_name=request.component_name.lower(),
            amount=request.amount,
            component_type="EARNINGS",
            month=request.month,
            pay_cycle=request.pay_cycle_type
        )
        db.add(setup)
        db.commit()
        
        # Get employee details and return full salary structure
        return PayrollService._get_full_salary_structure(db, employee_id)
    
    @staticmethod
    def add_deductions_component(db: Session, employee_id: str, request: ComponentRequest):
        from src.models.onboarding_process import OnboardingProcess
        
        # Add deductions component to payroll setup
        setup = PayrollSetup(
            employee_id=employee_id,
            component_name=request.component_name.lower(),
            amount=request.amount,
            component_type="DEDUCTIONS",
            month=request.month,
            pay_cycle=request.pay_cycle_type
        )
        db.add(setup)
        db.commit()
        
        # Get employee details and return full salary structure
        return PayrollService._get_full_salary_structure(db, employee_id)
    
    @staticmethod
    def update_component(db: Session, employee_id: str, request: ComponentRequest):
        # Update existing component
        setup = db.query(PayrollSetup).filter(
            PayrollSetup.employee_id == employee_id,
            PayrollSetup.component_name == request.component_name.lower()
        ).first()
        
        if setup:
            setup.amount = request.amount
            setup.month = request.month
            setup.pay_cycle = request.pay_cycle_type
            db.commit()
            db.refresh(setup)
        else:
            # If component doesn't exist, create it
            setup = PayrollSetup(
                employee_id=employee_id,
                component_name=request.component_name.lower(),
                amount=request.amount,
                component_type="EARNINGS",  # Default to earnings
                month=request.month,
                pay_cycle=request.pay_cycle_type
            )
            db.add(setup)
            db.commit()
        
        # Return full salary structure
        return PayrollService._get_full_salary_structure(db, employee_id)
    
    @staticmethod
    def get_employee_details(db: Session, employee_id: str):
        from src.models.onboarding_process import OnboardingProcess
        return db.query(OnboardingProcess).filter(OnboardingProcess.employee_id == employee_id).first()
    
    @staticmethod
    def get_all_employees(db: Session):
        from src.models.onboarding_process import OnboardingProcess
        return db.query(OnboardingProcess).all()
    
    @staticmethod
    def get_employee_summary(db: Session, employee_id: str):
        from src.models.onboarding_process import OnboardingProcess
        
        employee = db.query(OnboardingProcess).filter(OnboardingProcess.employee_id == employee_id).first()
        payroll_components = db.query(PayrollSetup).filter(PayrollSetup.employee_id == employee_id).all()
        
        earnings = sum(c.amount for c in payroll_components if c.component_type == "EARNINGS")
        deductions = sum(c.amount for c in payroll_components if c.component_type == "DEDUCTIONS")
        
        return {
            "employee": employee,
            "total_earnings": earnings,
            "total_deductions": deductions,
            "net_salary": earnings - deductions,
            "components": payroll_components
        }
    
    @staticmethod
    def _get_full_salary_structure(db: Session, employee_id: str):
        from src.models.onboarding_process import OnboardingProcess
        
        # Get employee details
        employee = db.query(OnboardingProcess).filter(
            OnboardingProcess.employee_id == employee_id
        ).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        annual_ctc = float(employee.annual_ctc)
        
        # Get all payroll components for this employee
        components = db.query(PayrollSetup).filter(
            PayrollSetup.employee_id == employee_id
        ).all()
        
        # Calculate base salary structure
        basic_salary = annual_ctc * 0.4 / 12
        hra = annual_ctc * 0.2 / 12
        allowance = annual_ctc * 0.4 / 12
        
        # Build earnings dictionary
        earnings_dict = {
            "basic_salary": basic_salary,
            "basic_salary_type": "Fixed",
            "hra": hra,
            "hra_type": "Fixed",
            "allowance": allowance,
            "allowance_type": "Fixed"
        }
        
        # Add custom earnings components
        for comp in components:
            if comp.component_type == "EARNINGS":
                earnings_dict[comp.component_name] = comp.amount
                earnings_dict[f"{comp.component_name}_type"] = "Fixed"
        
        # Build deductions dictionary
        provident_fund = basic_salary * 0.12
        professional_tax = 200
        
        deductions_dict = {
            "provident_fund": provident_fund,
            "provident_fund_type": "Percentage",
            "professional_tax": professional_tax,
            "professional_tax_type": "Fixed"
        }
        
        # Add custom deductions components
        for comp in components:
            if comp.component_type == "DEDUCTIONS":
                deductions_dict[comp.component_name] = comp.amount
                deductions_dict[f"{comp.component_name}_type"] = "Fixed"
        
        # Calculate totals
        total_earnings = sum(v for k, v in earnings_dict.items() if not k.endswith('_type'))
        total_deductions = sum(v for k, v in deductions_dict.items() if not k.endswith('_type'))
        net_salary = total_earnings - total_deductions
        
        return {
            "salary_structure": {
                "earnings": earnings_dict,
                "deductions": deductions_dict
            },
            "annual_ctc": annual_ctc,
            "total_earnings": total_earnings,
            "total_deductions": total_deductions,
            "net_salary": net_salary
        }