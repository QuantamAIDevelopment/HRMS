from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID
 
class PolicyCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    working_hours_per_day: float = Field(..., gt=0, le=24)
    working_days_per_week: int = Field(..., ge=1, le=7)
   
    # Timing Policy
    grace_period_minutes: int = Field(..., ge=0)
    mark_late_after_minutes: int = Field(..., ge=0)
    half_day_hours: float = Field(..., gt=0)
    auto_deduct_for_absence: bool
   
    # Overtime Policy
    overtime_enabled: bool
    overtime_multiplier_weekdays: Optional[float] = Field(None, gt=1.0)
    overtime_multiplier_weekend: Optional[float] = Field(None, gt=1.0)
   
    # Tracking Policy
    require_check_in: bool
    require_check_out: bool
   
    @validator('half_day_hours')
    def validate_half_day_hours(cls, v, values):
        if 'working_hours_per_day' in values and v >= values['working_hours_per_day']:
            raise ValueError('half_day_hours must be less than working_hours_per_day')
        return v
 
class PolicyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    working_hours_per_day: Optional[float] = Field(None, gt=0, le=24)
    working_days_per_week: Optional[int] = Field(None, ge=0, le=7)
   
    # Timing Policy
    grace_period_minutes: Optional[int] = Field(None, ge=0)
    mark_late_after_minutes: Optional[int] = Field(None, ge=0)
    half_day_hours: Optional[float] = Field(None, gt=0)
    auto_deduct_for_absence: Optional[bool] = None
   
    # Overtime Policy
    overtime_enabled: Optional[bool] = None
    overtime_multiplier_weekdays: Optional[float] = None
    overtime_multiplier_weekend: Optional[float] = None
   
    # Tracking Policy
    require_check_in: Optional[bool] = None
    require_check_out: Optional[bool] = None
 
class PolicyRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    working_hours_per_day: float
    working_days_per_week: int
    is_active: bool
   
    # Timing Policy
    grace_period_minutes: int
    mark_late_after_minutes: int
    half_day_hours: float
    auto_deduct_for_absence: bool
   
    # Overtime Policy
    overtime_enabled: bool
    overtime_multiplier_weekdays: Optional[float]
    overtime_multiplier_weekend: Optional[float]
   
    # Tracking Policy
    require_check_in: bool
    require_check_out: bool
   
    class Config:
        from_attributes = True
 
class PolicyListRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    working_hours_per_day: float
    working_days_per_week: int
    is_active: bool
   
    class Config:
        from_attributes = True
 
class PolicyActivateResponse(BaseModel):
    id: UUID
    is_active: bool
   
    class Config:
        from_attributes = True
 
class StandardPolicyUpdate(BaseModel):
    name: str = "Standard Policy"
    description: str = "Default attendance policy for regular employees."
    working_hours_per_day: float = 9
    working_days_per_week: int = 5
    grace_period_minutes: int = 15
    mark_late_after_minutes: int = 15
    half_day_hours: float = 4.5
    auto_deduct_for_absence: bool = True
    overtime_enabled: bool = True
    overtime_multiplier_weekdays: float = 1.5
    overtime_multiplier_weekend: float = 2
    require_check_in: bool = True
    require_check_out: bool = True
 
class FlexiblePolicyUpdate(BaseModel):
    name: str = "Flexible Policy"
    description: str = "Flexible working hours policy with relaxed timing rules."
    working_hours_per_day: float = 8
    working_days_per_week: int = 5
    grace_period_minutes: int = 30
    mark_late_after_minutes: int = 30
    half_day_hours: float = 4
    auto_deduct_for_absence: bool = False
    overtime_enabled: bool = False
    overtime_multiplier_weekdays: Optional[float] = None
    overtime_multiplier_weekend: Optional[float] = None
    require_check_in: bool = True
    require_check_out: bool = False