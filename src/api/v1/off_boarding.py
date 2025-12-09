from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from ...models.session import get_db
from ...models.off_boarding import OffBoarding
from ...schemas.off_boarding import OffBoardingCreate, OffBoardingResponse

router = APIRouter()

@router.post("/", response_model=OffBoardingResponse)
def create_off_boarding(off_boarding: OffBoardingCreate, db: Session = Depends(get_db)):
    # Get employee details to store in off_boarding
    emp_query = text("""
        SELECT CONCAT(e.first_name, ' ', e.last_name) as full_name,
               e.email_id, e.designation, d.department_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.department_id
        WHERE e.employee_id = :emp_id
    """)
    emp_result = db.execute(emp_query, {"emp_id": off_boarding.employee_id}).fetchone()
    
    data = off_boarding.dict()
    if emp_result:
        data['full_name'] = emp_result.full_name
        data['email'] = emp_result.email_id
        data['position'] = emp_result.designation
        data['department'] = emp_result.department_name
    
    db_obj = OffBoarding(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/all", response_model=List[OffBoardingResponse])
def get_all_off_boarding(db: Session = Depends(get_db)):
    query = text("""
        SELECT ob.id, ob.employee_id, ob.resignation_date, ob.last_working_day, ob.reason,
               ob.it_asset_return, ob.access_card_return, ob.knowledge_transfer, 
               ob.exit_interview, ob.final_settlement, ob.status, ob.created_at, ob.updated_at,
               COALESCE(CONCAT(e.first_name, ' ', e.last_name), ob.full_name) as employee_name,
               COALESCE(d.department_name, ob.department) as department,
               COALESCE(e.designation, ob.position) as designation
        FROM off_boarding ob
        LEFT JOIN employees e ON ob.employee_id = e.employee_id
        LEFT JOIN departments d ON e.department_id = d.department_id
        ORDER BY ob.resignation_date DESC
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@router.get("/cards")
def get_off_boarding_cards(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            COUNT(*) as total_exits,
            COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as active,
            COUNT(CASE WHEN status = 'INITIATED' THEN 1 END) as completed,
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
    try:
        off_boarding = db.query(OffBoarding).filter(OffBoarding.employee_id == employee_id).first()
        if not off_boarding:
            raise HTTPException(status_code=404, detail="Off-boarding not found")
        
        # Update fields
        update_data = off_boarding_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field != "employee_id":
                setattr(off_boarding, field, value)
        
        # Auto-update status to INITIATED when all checklist items are True
        if (off_boarding.it_asset_return and 
            off_boarding.access_card_return and 
            off_boarding.knowledge_transfer and 
            off_boarding.exit_interview and 
            off_boarding.final_settlement):
            off_boarding.status = "INITIATED"
        
        db.commit()
        db.refresh(off_boarding)
        
        # If status is INITIATED, delete employee from all tables
        if off_boarding.status == "INITIATED":
            try:
                db.execute(text("DELETE FROM time_entries WHERE employee_id = :emp_id"), {"emp_id": employee_id})
                db.execute(text("DELETE FROM employee_personal_details WHERE employee_id = :emp_id"), {"emp_id": employee_id})
                db.execute(text("DELETE FROM bank_details WHERE employee_id = :emp_id"), {"emp_id": employee_id})
                db.execute(text("DELETE FROM employee_work_experience WHERE employee_id = :emp_id"), {"emp_id": employee_id})
                db.execute(text("DELETE FROM employee_documents WHERE employee_id = :emp_id"), {"emp_id": employee_id})
                db.execute(text("DELETE FROM leave_management WHERE employee_id = :emp_id"), {"emp_id": employee_id})
                db.execute(text("DELETE FROM profile_edit_requests WHERE employee_id = :emp_id"), {"emp_id": employee_id})
                db.execute(text("UPDATE assets SET assigned_employee_id = NULL, status = 'Available' WHERE assigned_employee_id = :emp_id"), {"emp_id": employee_id})
                db.execute(text("DELETE FROM employees WHERE employee_id = :emp_id"), {"emp_id": employee_id})
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Error deleting employee: {str(e)}")
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"Error removing employee: {str(e)}")
        
        return {
            "message": "Off-boarding updated successfully",
            "status": off_boarding.status,
            "employee_id": off_boarding.employee_id,
            "it_asset_return": off_boarding.it_asset_return,
            "access_card_return": off_boarding.access_card_return,
            "knowledge_transfer": off_boarding.knowledge_transfer,
            "exit_interview": off_boarding.exit_interview,
            "final_settlement": off_boarding.final_settlement
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in update_off_boarding: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
