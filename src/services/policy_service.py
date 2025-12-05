from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List, Optional
from uuid import UUID
import logging
 
from ..models.policy import Policy
from ..schemas.policy import PolicyCreate, PolicyUpdate
 
logger = logging.getLogger(__name__)
 
class PoliciesService:
    def __init__(self, db: Session):
        self.db = db
 
    def get_all_policies(self) -> List[Policy]:
        return self.db.query(Policy).all()
 
    def get_policy_by_id(self, policy_id: UUID) -> Optional[Policy]:
        return self.db.query(Policy).filter(Policy.id == policy_id).first()
 
    def get_policy_by_name(self, policy_name: str) -> Optional[Policy]:
        return self.db.query(Policy).filter(Policy.name == policy_name).first()
 
    def create_policy(self, policy_data: PolicyCreate) -> Policy:
        try:
            policy = Policy(**policy_data.dict())
            self.db.add(policy)
            self.db.commit()
            self.db.refresh(policy)
            return policy
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Policy name already exists")
 
    def update_policy(self, policy_id: UUID, policy_data: PolicyUpdate) -> Optional[Policy]:
        policy = self.get_policy_by_id(policy_id)
        if not policy:
            return None
 
        try:
            for field, value in policy_data.dict(exclude_unset=True).items():
                setattr(policy, field, value)
           
            self.db.add(policy)
            self.db.flush()
            self.db.commit()
            self.db.refresh(policy)
            return policy
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Policy name already exists")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
 
    def update_policy_by_name(self, policy_name: str, policy_data: PolicyUpdate) -> Optional[Policy]:
        policy = self.db.query(Policy).filter(Policy.name == policy_name).first()
        if not policy:
            return None
 
        try:
            update_dict = policy_data.dict(exclude_unset=True, exclude_none=False)
           
            for field, value in update_dict.items():
                if field == 'working_days_per_week' and value == 0:
                    continue
                setattr(policy, field, value)
 
            self.db.add(policy)
            self.db.flush()
            self.db.commit()
            self.db.refresh(policy)
            return policy
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
 
    def activate_policy(self, policy_id: UUID) -> Optional[Policy]:
        policy = self.get_policy_by_id(policy_id)
        if not policy:
            return None
 
        # Deactivate all other policies
        self.db.query(Policy).update({Policy.is_active: False})
       
        # Activate the selected policy
        policy.is_active = True
        self.db.commit()
        self.db.refresh(policy)
        return policy
 
    def delete_policy(self, policy_id: UUID) -> bool:
        policy = self.get_policy_by_id(policy_id)
        if not policy:
            return False
 
        self.db.delete(policy)
        self.db.commit()
        return True