from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from src.core.security import create_access_token, verify_password, get_password_hash
from src.models.user import User
from src.api.deps import get_current_user, get_db
from src.config.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from src.services.token_service import TokenService
from datetime import timedelta

router = APIRouter(tags=["Authentication"])

# EXACT SCHEMAS AS REQUESTED
class VerifyOtpRequest(BaseModel):
    otp: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str
    confirm_password: str

# Other schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class MessageResponse(BaseModel):
    message: str
    success: bool = True

class LoginResponse(BaseModel):
    user_id: str
    employee_id: str
    email: str
    full_name: str
    role: str
    access_token: str
    refresh_token: str
    redirect_url: str
    token_type: str = "bearer"
    expires_in: int

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "employee_id": user.employee_id,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name
        }
    )
    
    refresh_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "email": user.email,
            "type": "refresh"
        },
        expires_delta=timedelta(days=7)
    )
    
    if user.role == "HR":
        redirect_url = "/hr/profile"
    elif user.role == "MANAGER":
        redirect_url = "/manager/profile"
    elif user.role == "EMPLOYEE":
        redirect_url = "/employee/profile"
    else:
        redirect_url = "/employee/profile"
    
    return LoginResponse(
        user_id=str(user.user_id),
        employee_id=user.employee_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        access_token=access_token,
        refresh_token=refresh_token,
        redirect_url=redirect_url,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return MessageResponse(message="If the email exists, an OTP has been sent")
    
    success = TokenService.create_and_send_otp(db, request.email)
    
    if success:
        return MessageResponse(message="OTP sent to your email")
    else:
        return MessageResponse(message="Failed to send OTP")

@router.post("/verify-otp", response_model=MessageResponse)
def verify_otp(request: VerifyOtpRequest):
    """Verify OTP - Only requires OTP field"""
    if len(request.otp) == 6 and request.otp.isdigit():
        return MessageResponse(message="OTP verified successfully")
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP format")

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset Password - Requires email, new_password, confirm_password"""
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirm password do not match")
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return MessageResponse(message="Password reset successfully")

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.put("/change-password", response_model=MessageResponse)
def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Change Password - Requires current_password, new_password"""
    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters long")
    
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    if verify_password(request.new_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="New password cannot be the same as current password")
    
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return MessageResponse(message="Password changed successfully")

@router.post("/logout", response_model=MessageResponse)
def logout():
    """Logout - No parameters required"""
    return MessageResponse(message="Logged out successfully")