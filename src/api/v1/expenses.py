from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.schemas.expense import ExpenseResponse
from src.services.expense_service import ExpenseService
from decimal import Decimal
from datetime import date
import os

router = APIRouter()

@router.post("/employee-expenses", response_model=ExpenseResponse)
def create_expense_request(
    employee_id: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    amount: Decimal = Form(...),
    expense_date: date = Form(...),
    receipt_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Save uploaded file (optional - file saved but path not stored in DB)
        if receipt_file:
            upload_dir = "uploads/receipts"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = f"{upload_dir}/{receipt_file.filename}"
            with open(file_path, "wb") as buffer:
                buffer.write(receipt_file.file.read())
        
        return ExpenseService.create_expense_with_file(
            db, employee_id, category, description, amount, expense_date, None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating expense: {str(e)}")

@router.get("/employee-expenses")
def get_all_expenses(db: Session = Depends(get_db)):
    try:
        return ExpenseService.get_all_expenses(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching expenses: {str(e)}")

@router.get("/employee-expenses/{expense_id}")
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = ExpenseService.get_expense_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.get("/employee-expenses/employee/{employee_id}")
def get_employee_expenses(employee_id: str, db: Session = Depends(get_db)):
    return ExpenseService.get_expenses_by_employee(db, employee_id)

@router.put("/employee-expenses/update-status")
def update_expense_status(
    expense_code: str = Form(...),
    employee_id: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    expense = ExpenseService.update_expense_status(db, expense_code, employee_id, status)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": f"Expense {status.lower()} successfully", "expense": expense}