from sqlalchemy.orm import Session
from src.models.Employee_models import (
    Employee, EmployeePersonalDetails, BankDetails, 
    Assets, EducationalQualifications, EmployeeDocuments
)
from src.schemas.Onboarding_schemas import (
    EmployeeCreate, PersonalDetailsCreate, BankDetailsCreate,
    AssetsCreate, EducationCreate, DocumentsCreate
)
from typing import List, Optional

class UnifiedEmployeeService:
    
    # ============================================================
    # EMPLOYEE SERVICES
    # ============================================================
    
    @staticmethod
    def create_employee(db: Session, employee_data: EmployeeCreate) -> Employee:
        db_employee = Employee(**employee_data.dict(exclude={'full_name'}))
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    
    @staticmethod
    def get_employee(db: Session, employee_id: str) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.employee_id == employee_id).first()
    
    @staticmethod
    def get_all_employees(db: Session) -> List[Employee]:
        return db.query(Employee).all()
    
    # ============================================================
    # PERSONAL DETAILS SERVICES
    # ============================================================
    
    @staticmethod
    def create_personal_details(db: Session, details_data: PersonalDetailsCreate) -> EmployeePersonalDetails:
        db_details = EmployeePersonalDetails(**details_data.dict())
        db.add(db_details)
        db.commit()
        db.refresh(db_details)
        return db_details
    
    @staticmethod
    def get_personal_details(db: Session, employee_id: str) -> Optional[EmployeePersonalDetails]:
        return db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
    
    @staticmethod
    def update_personal_details(db: Session, employee_id: str, details_data: dict) -> Optional[EmployeePersonalDetails]:
        db_details = db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
        if db_details:
            for field, value in details_data.items():
                if hasattr(db_details, field):
                    setattr(db_details, field, value)
            db.commit()
            db.refresh(db_details)
        return db_details
    
    # ============================================================
    # BANK DETAILS SERVICES
    # ============================================================
    
    @staticmethod
    def create_bank_details(db: Session, bank_data: BankDetailsCreate) -> BankDetails:
        db_bank = BankDetails(**bank_data.dict())
        db.add(db_bank)
        db.commit()
        db.refresh(db_bank)
        return db_bank
    
    @staticmethod
    def get_bank_details(db: Session, employee_id: str) -> Optional[BankDetails]:
        return db.query(BankDetails).filter(BankDetails.employee_id == employee_id).first()
    
    # ============================================================
    # ASSETS SERVICES
    # ============================================================
    
    @staticmethod
    def create_asset(db: Session, asset_data: AssetsCreate) -> Assets:
        db_asset = Assets(**asset_data.dict())
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        return db_asset
    
    @staticmethod
    def get_available_assets(db: Session) -> List[Assets]:
        return db.query(Assets).filter(Assets.status == "Available").all()
    
    @staticmethod
    def assign_asset(db: Session, asset_id: int, employee_id: str) -> Optional[Assets]:
        db_asset = db.query(Assets).filter(Assets.asset_id == asset_id).first()
        if db_asset:
            db_asset.assigned_employee_id = employee_id
            db_asset.status = "Assigned"
            db.commit()
            db.refresh(db_asset)
        return db_asset
    
    # ============================================================
    # EDUCATION SERVICES
    # ============================================================
    
    @staticmethod
    def create_education(db: Session, education_data: EducationCreate) -> EducationalQualifications:
        db_education = EducationalQualifications(**education_data.dict())
        db.add(db_education)
        db.commit()
        db.refresh(db_education)
        return db_education
    
    @staticmethod
    def get_employee_education(db: Session, employee_id: str) -> List[EducationalQualifications]:
        return db.query(EducationalQualifications).filter(EducationalQualifications.employee_id == employee_id).all()
    
    # ============================================================
    # DOCUMENTS SERVICES
    # ============================================================
    
    @staticmethod
    def create_document(db: Session, document_data: DocumentsCreate) -> EmployeeDocuments:
        db_document = EmployeeDocuments(**document_data.dict())
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    
    @staticmethod
    def get_employee_documents(db: Session, employee_id: str) -> List[EmployeeDocuments]:
        return db.query(EmployeeDocuments).filter(EmployeeDocuments.employee_id == employee_id).all()
    
    # ============================================================
    # COMPREHENSIVE EMPLOYEE DATA
    # ============================================================
    
    @staticmethod
    def get_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
        return db.query(Employee).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_employee(db: Session, employee_id: str, employee_data) -> Optional[Employee]:
        db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if db_employee:
            for field, value in employee_data.dict(exclude_unset=True).items():
                if hasattr(db_employee, field):
                    setattr(db_employee, field, value)
            db.commit()
            db.refresh(db_employee)
        return db_employee
    
    @staticmethod
    def delete_employee(db: Session, employee_id: str) -> bool:
        db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if db_employee:
            db.delete(db_employee)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_employee_full_profile(db: Session, employee_id: str) -> dict:
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            return None
        
        personal = db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
        bank = db.query(BankDetails).filter(BankDetails.employee_id == employee_id).first()
        education = db.query(EducationalQualifications).filter(EducationalQualifications.employee_id == employee_id).all()
        assets = db.query(Assets).filter(Assets.assigned_employee_id == employee_id).all()
        documents = db.query(EmployeeDocuments).filter(EmployeeDocuments.employee_id == employee_id).all()
        
        return {
            "employee": employee,
            "personal_details": personal,
            "bank_details": bank,
            "education": education,
            "assets": assets,
            "documents": documents
        }