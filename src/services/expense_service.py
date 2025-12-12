from sqlalchemy.orm import Session
from models.expense import Expense
from schemas.expense import ExpenseCreate
from datetime import datetime

class ExpenseService:
    @staticmethod
    def create_expense_with_file(db: Session, employee_id: str, category: str, description: str, amount, expense_date, file_path: str):
        try:
            print(f"DEBUG: Creating expense for employee_id: {employee_id}")
            print(f"DEBUG: Category: {category}, Amount: {amount}, Date: {expense_date}")
            
            db_expense = Expense(
                employee_id=employee_id,
                category=category,
                description=description,
                amount=amount,
                expense_date=expense_date,
                receipt_url=file_path,
                status="PENDING"
            )
            db.add(db_expense)
            db.commit()
            db.refresh(db_expense)
            
            print(f"DEBUG: Expense created successfully with ID: {db_expense.expense_id}")
            print(f"DEBUG: Stored employee_id: {db_expense.employee_id}")
            
            return db_expense
        except Exception as e:
            print(f"DEBUG: Error creating expense: {str(e)}")
            db.rollback()
            raise e
    
    @staticmethod
    def get_all_expenses(db: Session):
        return db.query(Expense).all()
    
    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int):
        return db.query(Expense).filter(Expense.expense_id == expense_id).first()
    
    @staticmethod
    def get_expenses_by_employee(db: Session, employee_id: str, status: str = None):
        print(f"DEBUG: Querying expenses for employee_id: {employee_id}, status: {status}")
        query = db.query(Expense).filter(Expense.employee_id == employee_id)
        if status:
            query = query.filter(Expense.status.ilike(f"%{status}%"))
        expenses = query.all()
        print(f"DEBUG: Found {len(expenses)} expenses for employee {employee_id}")
        for expense in expenses:
            print(f"DEBUG: Expense ID: {expense.expense_id}, Category: {expense.category}, Status: {expense.status}")
        return expenses
    
    @staticmethod
    def update_expense_status(db: Session, expense_id: str, employee_id: str, status: str):
        expense = db.query(Expense).filter(
            Expense.expense_id == int(expense_id),
            Expense.employee_id == employee_id
        ).first()
        if expense:
            expense.status = status
            db.commit()
            db.refresh(expense)
        return expense
    
    @staticmethod
    def get_expense_status_summary(db: Session):
        """Get overall expense status summary"""
        expenses = db.query(Expense).all()
        
        total_amount = sum(float(e.amount) for e in expenses)
        pending_amount = sum(float(e.amount) for e in expenses if e.status.upper() == "PENDING")
        approved_amount = sum(float(e.amount) for e in expenses if e.status.upper() == "APPROVED")
        rejected_amount = sum(float(e.amount) for e in expenses if e.status.upper() == "REJECTED")
        
        return {
            "Total Expenses": total_amount,
            "Pending Review": pending_amount,
            "Approved": approved_amount,
            "Rejected": rejected_amount
        }
    
    @staticmethod
    def get_employee_expense_status_summary(db: Session, employee_id: str):
        """Get expense status summary for specific employee"""
        expenses = db.query(Expense).filter(Expense.employee_id == employee_id).all()
        
        total_amount = sum(float(e.amount) for e in expenses)
        pending_amount = sum(float(e.amount) for e in expenses if e.status.upper() == "PENDING")
        approved_amount = sum(float(e.amount) for e in expenses if e.status.upper() == "APPROVED")
        rejected_amount = sum(float(e.amount) for e in expenses if e.status.upper() == "REJECTED")
        
        return {
            "Total Submitted": total_amount,
            "Pending Review": pending_amount,
            "Approved": approved_amount,
            "Rejected": rejected_amount
        }