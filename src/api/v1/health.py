from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from ...models.session import get_db

router = APIRouter()

@router.get("/health/db")
def check_database_connection(db: Session = Depends(get_db)):
    try:
        # Test basic connection
        db.execute(text("SELECT 1"))
        
        # Get all tables
        tables_result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in tables_result.fetchall()]
        
        # Get columns for key tables
        table_info = {}
        for table in ['employees', 'employees_personal', 'departments', 'attendance', 'leave_balance']:
            if table in tables:
                cols_result = db.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"))
                table_info[table] = [row[0] for row in cols_result.fetchall()]
        
        return {
            "status": "connected",
            "message": "Database connection successful",
            "all_tables": tables,
            "table_columns": table_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")