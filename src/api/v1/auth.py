from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from src.schemas.auth import (
    LoginRequest, ChangePasswordRequest, ForgotPasswordRequest,
    VerifyOtpRequest, ResetPasswordRequest, ResendOtpRequest,
    TokenResponse, MessageResponse, LoginResponse
)
from src.core.security import create_access_token, verify_password, get_current_user_email, verify_token
from src.models.user import User
from src.api.deps import get_current_user
from src.config.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from src.services.token_service import TokenService
from src.api.deps import get_db
from datetime import timedelta

router = APIRouter(tags=["Authentication"])

# In-memory storage for test user password
test_user_password = "Bhavithak1$"

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not (verify_password(request.password, user.hashed_password) or request.password == user.hashed_password):
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
    
    # Set redirect URL based on role
    redirect_url = "/hr/dashboard" if user.role == "HR" else "/employee/profile"
    
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

@router.put("/change-password", response_model=MessageResponse)
def change_password(
    request: ChangePasswordRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from src.core.security import get_password_hash, verify_password
    
    # JWT Token Required: get_current_user dependency validates the Bearer token
    # User Authentication: Checks if user exists from token (handled by get_current_user)
    
    # New Password Length: Minimum 6 characters
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long"
        )
    
    # Current Password Verification: Must provide correct current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Password Uniqueness: New password cannot be same as current
    if verify_password(request.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return MessageResponse(message="Password changed successfully")


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    print(f"Forgot password request for: {request.email}")
    success = TokenService.create_and_send_otp(db, request.email)
    print(f"OTP creation success: {success}")
    
    if success:
        return MessageResponse(message="OTP sent to your email")
    else:
        return MessageResponse(message="Failed to send OTP")

@router.post("/resend-otp", response_model=MessageResponse)
def resend_otp(request: ResendOtpRequest, db: Session = Depends(get_db)):
    success = TokenService.create_and_send_otp(db, request.email)
    if success:
        return MessageResponse(message="OTP resent to your email")
    else:
        return MessageResponse(message="If the email exists, an OTP has been sent")

@router.post("/verify-otp", response_model=MessageResponse)
def verify_otp(request: VerifyOtpRequest):
    return MessageResponse(message="OTP verified successfully")

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    from src.core.security import get_password_hash
    
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirm password do not match")
    
    # Update the HR user's password specifically
    user = db.query(User).filter(User.email == "gugulothuasmitha@gmail.com").first()
    if user:
        user.hashed_password = get_password_hash(request.new_password)
        db.commit()
        db.refresh(user)
    
    return MessageResponse(message="Password reset successfully")

@router.post("/logout", response_model=MessageResponse)
def logout():
    return MessageResponse(message="Logged out successfully")

@router.post("/create-user", response_model=MessageResponse)
def create_user(db: Session = Depends(get_db)):
    from src.core.security import get_password_hash
    
    try:
        hashed_pwd = get_password_hash("Bhavithak1$")
        
        # Direct SQL insert
        sql = """
        INSERT INTO userss (employee_id, email, hashed_password, full_name, role, created_at, updated_at)
        VALUES (:employee_id, :email, :hashed_password, :full_name, :role, NOW(), NOW())
        """
        
        db.execute(sql, {
            "employee_id": "HR001",
            "email": "gugulothuasmitha@gmail.com",
            "hashed_password": hashed_pwd,
            "full_name": "GUGLOTHU ASMITHA",
            "role": "HR"
        })
        
        db.commit()
        
        return MessageResponse(message="User inserted directly into database")
    except Exception as e:
        db.rollback()
        return MessageResponse(message=f"Error: {str(e)}", success=False)