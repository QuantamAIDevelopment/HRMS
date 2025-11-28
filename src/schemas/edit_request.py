from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class EditRequestBase(BaseModel):
    field_name: str
    old_value: Optional[str] = None
    new_value: str
    reason: Optional[str] = None

class EditRequestCreate(EditRequestBase):
    pass

class EditRequestResponse(EditRequestBase):
    id: int
    employee_id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True