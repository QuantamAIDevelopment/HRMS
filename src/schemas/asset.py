from pydantic import BaseModel
from datetime import date
from typing import Optional

class AssetCreate(BaseModel):
    asset_name: str
    asset_type: str
    serial_number: str
    status: str = "Available"
    employee_id: Optional[str] = None
    assigned_to: Optional[str] = None
    purchase_date: Optional[date] = None
    note: Optional[str] = None

class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    asset_type: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[str] = None
    employee_id: Optional[str] = None
    assigned_to: Optional[str] = None
    purchase_date: Optional[date] = None
    note: Optional[str] = None

class AssetResponse(BaseModel):
    asset_id: int
    asset_name: str
    asset_type: str
    serial_number: str
    status: str
    employee_id: Optional[str] = None
    assigned_to: Optional[str] = None
    purchase_date: Optional[date] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True

class AssetSummary(BaseModel):
    total_assets: int
    available: int
    assigned: int
    maintenance: int
    retired: int
