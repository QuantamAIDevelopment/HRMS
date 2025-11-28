from sqlalchemy.orm import Session
from src.models.expense import Expense
from src.schemas.expense import ExpenseCreate
from datetime import datetime

class ExpenseService:
    @staticmethod
    def create_expense_with_file(db: Session, employee_id: str, category: str, description: str, amount, expense_date, file_path: str):
        try:
            db_expense = Expense(
                employee_id=employee_id,
                category=category,
                description=description,
                amount=amount,
                expense_date=expense_date,
                status="PENDING"
            )
            db.add(db_expense)
            db.commit()
            db.refresh(db_expense)
            return db_expense
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def get_all_expenses(db: Session):
        return db.query(Expense).all()
    
    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int):
        return db.query(Expense).filter(Expense.expense_id == expense_id).first()
    
    @staticmethod
    def get_expenses_by_employee(db: Session, employee_id: str):
        return db.query(Expense).filter(Expense.employee_id == employee_id).all()
    
    @staticmethod
    def update_expense_status(db: Session, expense_code: str, employee_id: str, status: str):
        expense = db.query(Expense).filter(
            Expense.expense_code == expense_code,
            Expense.employee_id == employee_id
        ).first()
        if expense:
            expense.status = status
            db.commit()
            db.refresh(expense)
        return expense