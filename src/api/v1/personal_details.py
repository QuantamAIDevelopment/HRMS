from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_user
from models.user import User
from models.Employee_models import EmployeePersonalDetails
from schemas.personal_details import PersonalDetailsCreate, PersonalDetailsUpdate, PersonalDetailsResponse
import uuid

router = APIRouter()

@router.post("/personal-details", response_model=PersonalDetailsResponse)
def create_personal_details(
    details: PersonalDetailsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_details = EmployeePersonalDetails(
        **details.dict()
    )
    db.add(db_details)
    db.commit()
    db.refresh(db_details)
    return db_details

@router.get("/personal-details/{employee_id}", response_model=PersonalDetailsResponse)
def get_personal_details(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    details = db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
    if not details:
        raise HTTPException(status_code=404, detail="Personal details not found")
    return details

@router.put("/personal-details/{employee_id}", response_model=PersonalDetailsResponse)
def update_personal_details(
    employee_id: str,
    details_update: PersonalDetailsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_details = db.query(EmployeePersonalDetails).filter(EmployeePersonalDetails.employee_id == employee_id).first()
    if not db_details:
        raise HTTPException(status_code=404, detail="Personal details not found")
    
    for field, value in details_update.dict(exclude_unset=True).items():
        setattr(db_details, field, value)
    
    db.commit()
    db.refresh(db_details)
    return db_details