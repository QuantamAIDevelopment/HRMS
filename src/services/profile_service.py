from sqlalchemy.orm import Session
from ..models.employee_profile import Employee, ProfileEditRequest, EmployeePersonalDetails, BankDetails
from ..schemas.edit_request import EditRequestCreate
from ..schemas.profile import ProfileUpdate

class ProfileService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def get_employee_by_id(db: Session, employee_id: str):
        return db.query(Employee).filter(Employee.employee_id == employee_id).first()

    @staticmethod
    def calculate_completion_percentage(employee):
        # Simple completion calculation
        fields = [employee.first_name, employee.last_name, employee.email_id, employee.phone_number]
        completed = sum(1 for field in fields if field)
        return int((completed / len(fields)) * 100)

    @staticmethod
    def update_employee_basic(db: Session, employee_id: str, profile_data: ProfileUpdate):
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if employee:
            for field, value in profile_data.dict(exclude_unset=True).items():
                setattr(employee, field, value)
            db.commit()
            db.refresh(employee)
        return employee

    @staticmethod
    def update_personal_details(db: Session, employee_id: str, personal_data: dict):
        personal_details = db.query(EmployeePersonalDetails).filter(
            EmployeePersonalDetails.employee_id == employee_id
        ).first()
        if personal_details:
            for field, value in personal_data.items():
                setattr(personal_details, field, value)
            db.commit()
        return personal_details

    @staticmethod
    def update_bank_details(db: Session, employee_id: str, bank_data: dict):
        bank_details = db.query(BankDetails).filter(
            BankDetails.employee_id == employee_id
        ).first()
        if bank_details:
            for field, value in bank_data.items():
                setattr(bank_details, field, value)
            db.commit()
        return bank_details

    @staticmethod
    def request_profile_edit(db: Session, employee_id: str, edit_request: EditRequestCreate):
        request = ProfileEditRequest(
            employee_id=employee_id,
            **edit_request.dict()
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def get_pending_requests_for_manager(db: Session, manager_id: str):
        return db.query(ProfileEditRequest).filter(ProfileEditRequest.status == "pending").all()

    @staticmethod
    def approve_edit_request(db: Session, request_id: int, manager_id: str, comments: str = None):
        request = db.query(ProfileEditRequest).filter(ProfileEditRequest.id == request_id).first()
        if request:
            request.status = "approved"
            request.manager_comments = comments
            db.commit()
            db.refresh(request)
        return request

    @staticmethod
    def reject_edit_request(db: Session, request_id: int, manager_id: str, comments: str):
        request = db.query(ProfileEditRequest).filter(ProfileEditRequest.id == request_id).first()
        if request:
            request.status = "rejected"
            request.manager_comments = comments
            db.commit()
            db.refresh(request)
        return request