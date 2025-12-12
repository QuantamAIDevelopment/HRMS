from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from src.models.session import get_db
from src.models.off_boarding import OffBoarding
from src.schemas.off_boarding import OffBoardingCreate, OffBoardingResponse

router = APIRouter()

@router.post("/", response_model=OffBoardingResponse)
def create_off_boarding(off_boarding: OffBoardingCreate, db: Session = Depends(get_db)):
    db_obj = OffBoarding(**off_boarding.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/all", response_model=List[OffBoardingResponse])
def get_all_off_boarding(db: Session = Depends(get_db)):
    query = text("""
        SELECT ob.id, ob.employee_id, ob.resignation_date, ob.last_working_day, ob.reason,
               ob.status, ob.it_asset_return, ob.access_card_return, ob.knowledge_transfer, 
               ob.exit_interview, ob.final_settlement, ob.created_at, ob.updated_at,
               ob.full_name as employee_name, ob.department, ob.position as designation
        FROM off_boarding ob
        ORDER BY ob.resignation_date DESC
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@router.get("/cards")
def get_off_boarding_cards(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            COUNT(*) as total_exits,
            COUNT(CASE WHEN UPPER(TRIM(status)) = 'IN_PROGRESS' THEN 1 END) as active,
            COUNT(CASE WHEN UPPER(TRIM(status)) = 'INITIATED' THEN 1 END) as completed,
            ROUND(AVG(
                (CASE WHEN it_asset_return THEN 1 ELSE 0 END +
                 CASE WHEN access_card_return THEN 1 ELSE 0 END +
                 CASE WHEN knowledge_transfer THEN 1 ELSE 0 END +
                 CASE WHEN exit_interview THEN 1 ELSE 0 END +
                 CASE WHEN final_settlement THEN 1 ELSE 0 END) * 100.0 / 5
            ), 1) as avg_clearance
        FROM off_boarding
    """)
    result = db.execute(query).fetchone()
    return {
        "total_exits": result.total_exits or 0,
        "active": result.active or 0,
        "completed": result.completed or 0,
        "avg_clearance": float(result.avg_clearance) if result.avg_clearance else 0.0
    }

@router.put("/{employee_id}")
def update_off_boarding(employee_id: str, off_boarding_update: OffBoardingCreate, db: Session = Depends(get_db)):
    """Update off-boarding clearance checklist and status"""
    off_boarding = db.query(OffBoarding).filter(OffBoarding.employee_id == employee_id).first()
    if not off_boarding:
        raise HTTPException(status_code=404, detail="Off-boarding not found")
    
    # Update fields
    update_data = off_boarding_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field != "employee_id":  # Don't update employee_id
            setattr(off_boarding, field, value)
    
    # Auto-update status to INITIATED if all checklist items are True and status is PENDING
    if (off_boarding.status == "PENDING" and 
        off_boarding.it_asset_return and 
        off_boarding.access_card_return and 
        off_boarding.knowledge_transfer and 
        off_boarding.exit_interview and 
        off_boarding.final_settlement):
        off_boarding.status = "INITIATED"
    
    # If status is INITIATED, delete employee from all tables
    if off_boarding.status == "INITIATED":
        try:
            # Remove employee from all related tables
            tables_to_clean = [
                "time_entries",
                "employee_personal_details", 
                "bank_details",
                "employee_work_experience",
                "employee_documents",
                "leave_management",
                "profile_edit_requests"
            ]
            
            for table in tables_to_clean:
                db.execute(
                    text(f"DELETE FROM {table} WHERE employee_id = :emp_id"),
                    {"emp_id": employee_id}
                )
            
            # Update assets to unassign from employee
            db.execute(
                text("UPDATE assets SET employee_id = NULL, assigned_to = NULL, status = 'Available' WHERE employee_id = :emp_id"),
                {"emp_id": employee_id}
            )
            
            # Remove from users table
            db.execute(
                text("DELETE FROM users WHERE employee_id = :emp_id"),
                {"emp_id": employee_id}
            )
            
            # Get employee details before deletion for count updates
            emp_details = db.execute(
                text("SELECT designation, shift_id FROM employees WHERE employee_id = :emp_id"),
                {"emp_id": employee_id}
            ).fetchone()
            
            # Finally remove from employees table
            db.execute(
                text("DELETE FROM employees WHERE employee_id = :emp_id"),
                {"emp_id": employee_id}
            )
            
            # Update job_titles employee count
            if emp_details:
                db.execute(
                    text("UPDATE job_titles SET employees = (SELECT COUNT(*) FROM employees WHERE designation = job_titles.job_title) WHERE job_title = :designation"),
                    {"designation": emp_details.designation}
                )
                
                # Update shift_master employee count
                db.execute(
                    text("UPDATE shift_master SET employees = (SELECT COUNT(*) FROM employees WHERE shift_id = shift_master.shift_id) WHERE shift_id = :shift_id"),
                    {"shift_id": emp_details.shift_id}
                )
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error removing employee: {str(e)}")
    
    db.commit()
    db.refresh(off_boarding)
    return {"message": "Off-boarding updated successfully", "off_boarding": off_boarding}
