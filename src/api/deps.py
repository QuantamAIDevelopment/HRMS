from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.security import verify_token, CurrentUser, get_current_user
from src.models.session import get_db
from sqlalchemy.orm import Session

security = HTTPBearer()

async def get_current_user_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    """Get current user from JWT token"""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    email = verify_token(credentials.credentials)
    return CurrentUser(user_id=1, email=email, role="HR Manager")

async def get_db_dependency() -> Session:
    """Get database session"""
    return get_db()
