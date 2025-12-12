from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from src.models.Employee_models import Assets as Asset
from src.schemas.asset import AssetCreate, AssetUpdate, AssetResponse, AssetSummary
from datetime import date

class AssetService:
    @staticmethod
    def create_asset(db: Session, asset: AssetCreate) -> AssetResponse:
        existing_asset = db.query(Asset).filter(Asset.serial_number == asset.serial_number).first()
        if existing_asset:
            raise ValueError(f"Asset with serial number '{asset.serial_number}' already exists")
        if not asset.condition:
            raise ValueError("condition is required")
        
        if asset.status == "Assigned":
            if not asset.employee_id or not asset.assigned_to:
                raise ValueError("employee_id and assigned_to are required when status is Assigned")
        elif asset.status == "Available":
            asset.employee_id = None
            asset.assigned_to = None
            
        db_asset = Asset(**asset.dict())
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        return AssetResponse(**db_asset.__dict__)

    @staticmethod
    def get_assets(db: Session, search: Optional[str] = None, status: Optional[str] = None, asset_type: Optional[str] = None, employee_id: Optional[str] = None) -> List[AssetResponse]:
        query = db.query(Asset)
        if search:
            query = query.filter((Asset.asset_name.ilike(f"%{search}%")) | (Asset.serial_number.ilike(f"%{search}%")))
        if status:
            query = query.filter(Asset.status == status)
        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)
        if employee_id:
            query = query.filter(Asset.employee_id == employee_id)
        assets = query.order_by(Asset.asset_id.desc()).all()
        return [AssetResponse(**asset.__dict__) for asset in assets]

    @staticmethod
    def get_asset_by_serial(db: Session, serial_number: str) -> Optional[AssetResponse]:
        asset = db.query(Asset).filter(Asset.serial_number == serial_number).first()
        return AssetResponse(**asset.__dict__) if asset else None

    @staticmethod
    def delete_asset(db: Session, asset_id: int) -> bool:
        asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
        if asset:
            db.delete(asset)
            db.commit()
            return True
        return False

    @staticmethod
    def return_asset(db: Session, asset_id: int) -> Optional[AssetResponse]:
        asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
        if asset and asset.status == "Assigned":
            asset.status = "Available"
            asset.employee_id = None
            asset.assigned_to = None
            db.commit()
            db.refresh(asset)
            return AssetResponse(**asset.__dict__)
        return None

    @staticmethod
    def get_asset_types(db: Session) -> List[str]:
        types = db.query(Asset.asset_type).distinct().all()
        return [t[0] for t in types if t[0]]

    @staticmethod
    def get_summary(db: Session) -> AssetSummary:
        total = db.query(Asset).count()
        available = db.query(Asset).filter(Asset.status == "Available").count()
        assigned = db.query(Asset).filter(Asset.status == "Assigned").count()
        maintenance = db.query(Asset).filter(Asset.status == "Maintenance").count()
        retired = db.query(Asset).filter(Asset.status == "Retired").count()
        return AssetSummary(total_assets=total, available=available, assigned=assigned, maintenance=maintenance, retired=retired)

    @staticmethod
    def get_assets_history(db: Session) -> List[dict]:
        assets = db.query(Asset).order_by(Asset.created_at.desc()).all()
        return [asset.__dict__ for asset in assets]
