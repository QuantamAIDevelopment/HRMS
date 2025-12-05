from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from enum import Enum

class PolicyName(str, Enum):
    STANDARD = "Standard Policy"
    FLEXIBLE = "Flexible Policy"

from ...models.session import get_db
from ...services.policies_service import PoliciesService
from ...schemas.policy import (
    PolicyListRead, PolicyRead, PolicyCreate, PolicyUpdate, PolicyActivateResponse,
    StandardPolicyUpdate, FlexiblePolicyUpdate
)

router = APIRouter(prefix="/api/standard-policy", tags=["standard-policy"])

@router.get("/", response_model=List[PolicyListRead])
def get_policies(db: Session = Depends(get_db)):
    service = PoliciesService(db)
    policies = service.get_all_policies()
    return policies

@router.get("/by-name/{policy_name}", response_model=PolicyRead)
def get_policy_by_name(policy_name: PolicyName, db: Session = Depends(get_db)):
    service = PoliciesService(db)
    policy = service.get_policy_by_name(policy_name)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy



@router.put("/Standard Policy", response_model=PolicyRead)
def update_standard_policy(policy_data: StandardPolicyUpdate, db: Session = Depends(get_db)):
    service = PoliciesService(db)
    # Convert to PolicyUpdate for service compatibility
    update_data = PolicyUpdate(**policy_data.dict())
    policy = service.update_policy_by_name("Standard Policy", update_data)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.put("/Flexible Policy", response_model=PolicyRead)
def update_flexible_policy(policy_data: FlexiblePolicyUpdate, db: Session = Depends(get_db)):
    service = PoliciesService(db)
    # Convert to PolicyUpdate for service compatibility
    update_data = PolicyUpdate(**policy_data.dict())
    policy = service.update_policy_by_name("Flexible Policy", update_data)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

