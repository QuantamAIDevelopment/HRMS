from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from enum import Enum
 
class PolicyName(str, Enum):
    STANDARD = "Standard Policy"
    FLEXIBLE = "Flexible Policy"
 
from ...models.session import get_db
from ...services.policy_service import PoliciesService
from ...schemas.policy import (
    PolicyListRead, PolicyRead, PolicyCreate, PolicyUpdate, PolicyActivateResponse,
    StandardPolicyUpdate, FlexiblePolicyUpdate
)
 
router = APIRouter(prefix="/api/v1/standard-policy", tags=["standard-policy"])
 
@router.get("/", response_model=List[PolicyRead])
def get_policies(db: Session = Depends(get_db)):
    service = PoliciesService(db)
    policies = service.get_all_policies()
    return policies
 
@router.post("/", response_model=PolicyRead, status_code=status.HTTP_201_CREATED)
def create_policy(policy_data: PolicyCreate, db: Session = Depends(get_db)):
    try:
        service = PoliciesService(db)
        policy = service.create_policy(policy_data)
        return policy
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
 