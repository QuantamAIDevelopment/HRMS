from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, Query
from sqlalchemy.orm import Session
from api.deps import get_db
from schemas.expense import ExpenseResponse, ExpenseStatusResponse
from services.expense_service import ExpenseService
from decimal import Decimal
from datetime import date

router = APIRouter()

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
        if receipt_file and receipt_file.filename:
            file_content = receipt_file.file.read()
            receipt_base64 = base64.b64encode(file_content).decode('utf-8')
            print(f"DEBUG: File uploaded, base64 length: {len(receipt_base64)}")
        else:
            print("DEBUG: No file uploaded")
        
        expense = ExpenseService.create_expense_with_file(
            db, employee_id, category, description, amount, expense_date, receipt_base64
        )
        print(f"DEBUG: Created expense with receipt_url: {expense.receipt_url}")
        
        # Convert receipt_url from bytes to string if it exists
        receipt_url_str = None
        if hasattr(expense, 'receipt_url') and expense.receipt_url is not None:
            try:
                if isinstance(expense.receipt_url, bytes):
                    receipt_url_str = expense.receipt_url.decode('utf-8')
                elif isinstance(expense.receipt_url, memoryview):
                    receipt_url_str = expense.receipt_url.tobytes().decode('utf-8')
                else:
                    receipt_url_str = str(expense.receipt_url)
            except Exception as e:
                print(f"DEBUG: Error converting receipt_url: {e}")
                receipt_url_str = str(expense.receipt_url)
        
        print(f"DEBUG: Final receipt_url_str: {receipt_url_str}")
        print(f"DEBUG: expense object attributes: {dir(expense)}")
        
        # Force receipt_url to appear - set to "test" if None
        if receipt_url_str is None:
            receipt_url_str = "null_value_from_db"
        
        # Return dictionary directly to ensure receipt_url is always included
        response_dict = {
            "employee_id": expense.employee_id,
            "category": expense.category,
            "description": expense.description,
            "amount": str(expense.amount),
            "expense_date": expense.expense_date.isoformat(),
            "receipt_url": receipt_url_str,
            "expense_id": expense.expense_id,
            "status": expense.status,
            "created_at": expense.created_at.isoformat(),
            "updated_at": expense.updated_at.isoformat()
        }
        
        print(f"DEBUG: Response dict: {response_dict}")
        return response_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating expense: {str(e)}")

@router.get("/employee-expenses")
def get_all_expenses(db: Session = Depends(get_db)):
    try:
        return ExpenseService.get_all_expenses(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching expenses: {str(e)}")



@router.get("/employee-expenses/employee/{employee_id}")
def get_employee_expenses(employee_id: str, db: Session = Depends(get_db)):
    return ExpenseService.get_expenses_by_employee(db, employee_id)

@router.put("/employee-expenses/update-status")
def update_expense_status(
    expense_id: str = Form(...),
    employee_id: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    expense = ExpenseService.update_expense_status(db, expense_id, employee_id, status)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": f"Expense {status.lower()} successfully", "expense": expense}



@router.get("/expenses/status")
def get_expense_status(db: Session = Depends(get_db)):
    """Get overall expense status summary"""
    try:
        return ExpenseService.get_expense_status_summary(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching expense status: {str(e)}")

@router.get("/expenses/status/{employee_id}")
def get_employee_expense_status(employee_id: str, db: Session = Depends(get_db)):
    """Get expense status summary for specific employee"""
    try:
        return ExpenseService.get_employee_expense_status_summary(db, employee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching employee expense status: {str(e)}")

