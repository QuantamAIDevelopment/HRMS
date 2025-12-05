from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class AssetCreate(BaseModel):
    serial_number: Optional[str] = None
    asset_name: str
    asset_type: str
    assigned_employee_id: Optional[str] = None
    status: Optional[str] = "Available"
    condition: Optional[str] = "Good"
    purchase_date: Optional[date] = None
    value: Optional[Decimal] = None

class AssetUpdate(BaseModel):
    serial_number: Optional[str] = None
    asset_name: Optional[str] = None
    asset_type: Optional[str] = None
    assigned_employee_id: Optional[str] = None
    status: Optional[str] = None
    condition: Optional[str] = None
    purchase_date: Optional[date] = None
    value: Optional[Decimal] = None

class AssetResponse(BaseModel):
    asset_id: int
    serial_number: Optional[str]
    asset_name: str
    asset_type: str
    assigned_employee_id: Optional[str]
    status: str
    condition: str
    purchase_date: Optional[date]
    value: Optional[Decimal]

    class Config:
        from_attributes = True