from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

class CurrentUser:
    def __init__(self, user_id: int, email: str, role: str):
        self.user_id = user_id
        self.email = email
        self.role = role

# Stub for current user dependency - to be implemented by auth developer
def get_current_user() -> CurrentUser:
    # This is a stub - actual implementation will be provided by auth developer
    # For now, return a mock HR Manager for testing
    return CurrentUser(user_id=1, email="hr@company.com", role="HR Manager")

def require_hr_role(current_user: CurrentUser = Depends(get_current_user)):
    """Dependency to ensure user has HR Manager or HR Executive role"""
    if current_user.role not in ["HR Manager", "HR Executive"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. HR role required."
        )
    return current_user