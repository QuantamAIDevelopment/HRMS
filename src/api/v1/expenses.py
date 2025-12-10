from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, Query
from sqlalchemy.orm import Session
from api.deps import get_db
from schemas.expense import ExpenseResponse, ExpenseStatusResponse
from services.expense_service import ExpenseService
from decimal import Decimal
from datetime import date
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

def convert_receipt_url(receipt_url):
    if receipt_url is None:
        return None
    if isinstance(receipt_url, str):
        return receipt_url
    if isinstance(receipt_url, (bytes, memoryview)):
        if isinstance(receipt_url, memoryview):
            receipt_url = receipt_url.tobytes()
        try:
            return receipt_url.decode('utf-8')
        except UnicodeDecodeError:
            import base64
            return base64.b64encode(receipt_url).decode('utf-8')
    return None

class ExpenseResponseModel(BaseModel):
    employee_id: str
    category: str
    description: str
    amount: float
    expense_date: str
    receipt_url: Optional[str]
    expense_id: int
    status: str
    created_at: str
    updated_at: str

@router.post("/employee-expenses")
def create_expense_request(
    employee_id: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    amount: Decimal = Form(...),
    expense_date: date = Form(...),
    receipt_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        import base64
        receipt_base64 = None
        
        print(f"DEBUG: receipt_file = {receipt_file}")
        print(f"DEBUG: receipt_file.filename = {receipt_file.filename if receipt_file else 'None'}")
        
        if receipt_file and receipt_file.filename:
            file_content = receipt_file.file.read()
            print(f"DEBUG: file_content length = {len(file_content)}")
            if len(file_content) > 0:
                receipt_base64 = base64.b64encode(file_content).decode('utf-8')
                print(f"DEBUG: receipt_base64 length = {len(receipt_base64)}")
                print(f"DEBUG: receipt_base64 first 50 chars = {receipt_base64[:50]}")
            else:
                print("DEBUG: File content is empty")
                receipt_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        else:
            print("DEBUG: No file uploaded, using test base64")
            receipt_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        print(f"DEBUG: Calling service with receipt_base64 = {receipt_base64 is not None}")
        print(f"DEBUG: receipt_base64 type = {type(receipt_base64)}")
        
        # Ensure receipt_base64 is a string
        if receipt_base64 and not isinstance(receipt_base64, str):
            receipt_base64 = str(receipt_base64)
        
        expense = ExpenseService.create_expense_with_file(
            db, employee_id, category, description, amount, expense_date, receipt_base64
        )
        print(f"DEBUG: Service returned expense.receipt_url = {expense.receipt_url}")
        print(f"DEBUG: expense.receipt_url type = {type(expense.receipt_url)}")
        
        # Force refresh from database to check what was actually stored
        db.refresh(expense)
        print(f"DEBUG: After refresh - expense.receipt_url type = {type(expense.receipt_url)}")
        print(f"DEBUG: After refresh - first 50 chars = {str(expense.receipt_url)[:50] if expense.receipt_url else 'None'}")
        
        converted_receipt_url = convert_receipt_url(expense.receipt_url)
        print(f"DEBUG: converted_receipt_url = {converted_receipt_url is not None}")
        print(f"DEBUG: converted_receipt_url first 50 chars = {converted_receipt_url[:50] if converted_receipt_url else 'None'}")
        
        return {
            "employee_id": expense.employee_id,
            "category": expense.category,
            "description": expense.description,
            "amount": float(expense.amount),
            "expense_date": expense.expense_date.strftime('%Y-%m-%d'),
            "receipt_url": converted_receipt_url,
            "expense_id": expense.expense_id,
            "status": expense.status,
            "created_at": expense.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": expense.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating expense: {str(e)}")

@router.get("/employee-expenses")
def get_all_expenses(db: Session = Depends(get_db)):
    try:
        expenses = ExpenseService.get_all_expenses(db)
        return [{
            "employee_id": expense.employee_id,
            "category": expense.category,
            "description": expense.description,
            "amount": float(expense.amount),
            "expense_date": expense.expense_date.strftime('%Y-%m-%d'),
            "receipt_url": convert_receipt_url(expense.receipt_url),
            "expense_id": expense.expense_id,
            "status": expense.status,
            "created_at": expense.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": expense.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        } for expense in expenses]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching expenses: {str(e)}")



@router.get("/employee-expenses/employee/{employee_id}")
def get_employee_expenses(employee_id: str, db: Session = Depends(get_db)):
    try:
        expenses = ExpenseService.get_expenses_by_employee(db, employee_id)
        return [{
            "employee_id": expense.employee_id,
            "category": expense.category,
            "description": expense.description,
            "amount": float(expense.amount),
            "expense_date": expense.expense_date.strftime('%Y-%m-%d'),
            "receipt_url": convert_receipt_url(expense.receipt_url),
            "expense_id": expense.expense_id,
            "status": expense.status,
            "created_at": expense.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": expense.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        } for expense in expenses]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching employee expenses: {str(e)}")

@router.put("/employee-expenses/update-status")
def update_expense_status(
    expense_id: str = Form(...),
    employee_id: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        expense = ExpenseService.update_expense_status(db, expense_id, employee_id, status)
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        return {
            "message": f"Expense {status.lower()} successfully",
            "expense": {
                "employee_id": expense.employee_id,
                "category": expense.category,
                "description": expense.description,
                "amount": float(expense.amount),
                "expense_date": expense.expense_date.strftime('%Y-%m-%d'),
                "receipt_url": convert_receipt_url(expense.receipt_url),
                "expense_id": expense.expense_id,
                "status": expense.status,
                "created_at": expense.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": expense.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating expense status: {str(e)}")



@router.get("/expenses/status")
def get_expense_status(db: Session = Depends(get_db)):
    """Get overall expense status summary"""
    return ExpenseService.get_expense_status_summary(db)

@router.get("/expenses/status/{employee_id}")
def get_employee_expense_status(employee_id: str, db: Session = Depends(get_db)):
    """Get expense status summary for specific employee"""
    return ExpenseService.get_employee_expense_status_summary(db, employee_id)

@router.get("/debug/receipt-url/{expense_id}")
def debug_receipt_url(expense_id: int, db: Session = Depends(get_db)):
    """Debug endpoint to check raw receipt_url value in database"""
    expense = ExpenseService.get_expense_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Convert receipt_url to string for safe serialization
    receipt_url_str = convert_receipt_url(expense.receipt_url)
    
    return {
        "expense_id": expense.expense_id,
        "receipt_url_type": type(expense.receipt_url).__name__,
        "receipt_url_length": len(expense.receipt_url) if expense.receipt_url else 0,
        "is_string": isinstance(expense.receipt_url, str),
        "is_bytes": isinstance(expense.receipt_url, bytes),
        "is_memoryview": isinstance(expense.receipt_url, memoryview),
        "receipt_url_preview": receipt_url_str
    }



