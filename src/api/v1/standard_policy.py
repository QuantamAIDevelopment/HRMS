from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from enum import Enum
 
class PolicyName(str, Enum):
    STANDARD = "Standard Policy"
    FLEXIBLE = "Flexible Policy"
 
from src.models.session import get_db
from src.services.policy_service import PoliciesService
from src.schemas.policy import (
    PolicyListRead, PolicyRead, PolicyCreate, PolicyUpdate, PolicyActivateResponse,
    StandardPolicyUpdate, FlexiblePolicyUpdate
)
 
router = APIRouter(prefix="/api/v1/policy", tags=["policy"])
 
@router.get("/", response_model=List[PolicyRead])
def get_policies(db: Session = Depends(get_db)):
    service = PoliciesService(db)
    return service.get_all_policies()

@router.post("/")
def create_or_update_policy(
    policy_data: PolicyCreate,
    db: Session = Depends(get_db)
):
    service = PoliciesService(db)
    
    if not policy_data.name:
        raise HTTPException(status_code=400, detail="Policy name is required")
    
    # Try to update existing policy first
    policy = service.update_policy_by_name(policy_data.name, policy_data)
    
    # If policy doesn't exist, create it
    if not policy:
        policy = service.create_policy(policy_data)
    
    return policy
 