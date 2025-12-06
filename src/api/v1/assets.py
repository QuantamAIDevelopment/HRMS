from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.deps import get_db
from models.Employee_models import Assets

router = APIRouter()

@router.post("/available-assets")
def get_available_assets(db: Session = Depends(get_db)):
    available_assets = db.query(Assets.asset_type, Assets.serial_number).filter(Assets.status == "Available").all()
    
    asset_types_with_serials = {}
    for asset_type, serial_number in available_assets:
        if asset_type not in asset_types_with_serials:
            asset_types_with_serials[asset_type] = []
        if serial_number:
            asset_types_with_serials[asset_type].append(serial_number)
    
    return asset_types_with_serials