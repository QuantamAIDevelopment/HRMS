import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from src.config.settings import settings
import random
import string

security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')[:72]
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)

def get_password_hash(password):
    if isinstance(password, str):
        password = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')


class CurrentUser:
    def __init__(self, user_id: int, email: str, role: str):
        self.user_id = user_id
        self.email = email
        self.role = role

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "iat": int(now.timestamp())})
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("email")
        user_id: str = payload.get("sub")
        if email is None and user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return email if email else user_id
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token verification failed")

def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return verify_token(credentials.credentials)

def get_current_user() -> CurrentUser:
    """Stub for current user dependency - to be implemented by auth developer"""
    return CurrentUser(user_id=1, email="hr@company.com", role="HR Manager")

def require_hr_role(current_user: CurrentUser = Depends(get_current_user)):
    """Dependency to ensure user has HR Manager or HR Executive role"""
    if current_user.role not in ["HR Manager", "HR Executive"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. HR role required."
        )
    return current_user

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

def generate_reset_token(length: int = 32) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def map_designation_to_role(designation: str) -> str:
    """Map employee designation to appropriate user role"""
    designation_lower = designation.lower().replace(' ', '')
    
    # HR Manager variations (case-insensitive, with/without spaces)
    hr_manager_variations = ['hrmanager', 'hrmanger', 'hrmanager', 'humanresourcemanager']
    if any(var in designation_lower for var in hr_manager_variations):
        return "HR_MANAGER"
    
    # HR Executive variations (case-insensitive, with/without spaces)
    hr_executive_variations = ['hrexecutive', 'hrexctive', 'hrexective', 'humanresourceexecutive']
    if any(var in designation_lower for var in hr_executive_variations):
        return "HR_EXECUTIVE"
    
    # Manager variations (case-insensitive)
    manager_variations = ['manager', 'manger', 'head', 'director', 'lead', 'supervisor']
    if any(var in designation_lower for var in manager_variations):
        return "MANAGER"
    
    # Admin roles
    if any(keyword in designation_lower for keyword in ['admin', 'administrator']):
        return "ADMIN"
    
    # Default to employee
    return "EMPLOYEE"
