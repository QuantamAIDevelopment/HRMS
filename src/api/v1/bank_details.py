from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_user
from models.user import User
from models.Employee_models import BankDetails
from schemas.bank_details import BankDetailsCreate, BankDetailsUpdate, BankDetailsResponse
import uuid

router = APIRouter()

@router.post("/bank-details", response_model=BankDetailsResponse)
def create_bank_details(
    details: BankDetailsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_details = BankDetails(
        **details.dict()
    )
    db.add(db_details)
    db.commit()
    db.refresh(db_details)
    return db_details

@router.get("/bank-details/{employee_id}", response_model=BankDetailsResponse)
def get_bank_details(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    details = db.query(BankDetails).filter(BankDetails.employee_id == employee_id).first()
    if not details:
        raise HTTPException(status_code=404, detail="Bank details not found")
    return details

@router.put("/bank-details/{employee_id}", response_model=BankDetailsResponse)
def update_bank_details(
    employee_id: str,
    details_update: BankDetailsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_details = db.query(BankDetails).filter(BankDetails.employee_id == employee_id).first()
    if not db_details:
        raise HTTPException(status_code=404, detail="Bank details not found")
    
    for field, value in details_update.dict(exclude_unset=True).items():
        setattr(db_details, field, value)
    
    db.commit()
    db.refresh(db_details)
    return db_details