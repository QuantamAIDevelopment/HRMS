from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.session import get_db
from services.asset_service import AssetService
from schemas.asset import AssetCreate, AssetUpdate, AssetResponse, AssetSummary
from models.asset import Asset

router = APIRouter()

@router.post("/assets/", response_model=AssetResponse, tags=["Asset Management"])
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    try:
        return AssetService.create_asset(db, asset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assets/summary", response_model=AssetSummary, tags=["Asset Management"])
def get_assets_summary(db: Session = Depends(get_db)):
    try:
        return AssetService.get_summary(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assets/history", tags=["Asset Management"])
def get_assets_history(db: Session = Depends(get_db)):
    try:
        return AssetService.get_assets_history(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/assets/edit/{asset_id}", tags=["Asset Management"])
def edit_asset(asset_id: int, asset: AssetUpdate, db: Session = Depends(get_db)):
    try:
        target_asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
        if not target_asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        update_data = asset.dict(exclude_unset=True)
        update_data = {k: v for k, v in update_data.items() if v not in ['string', '', None]}
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid data to update")
        updated_fields = []
        for field, value in update_data.items():
            if hasattr(target_asset, field):
                setattr(target_asset, field, value)
                updated_fields.append(field)
        db.commit()
        db.refresh(target_asset)
        return {"message": "Asset updated successfully", "updated_fields": updated_fields, "asset": target_asset}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/assets/{asset_id}/return", response_model=AssetResponse, tags=["Asset Management"])
def return_asset(asset_id: int, db: Session = Depends(get_db)):
    try:
        returned_asset = AssetService.return_asset(db, asset_id)
        if not returned_asset:
            raise HTTPException(status_code=400, detail="Asset not assigned or not found")
        return returned_asset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/assets/{asset_id}", tags=["Asset Management"])
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    try:
        success = AssetService.delete_asset(db, asset_id)
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found")
        return {"message": "Asset deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))