from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from src.schemas.auth_new import (
    LoginRequest, SignupRequest, ChangePasswordRequest, ForgotPasswordRequest,
    VerifyOtpRequest, ResetPasswordRequest, ResendOtpRequest,
    TokenResponse, MessageResponse, LoginResponse
)
from src.core.security import create_access_token, verify_password, get_current_user_email, verify_token
from src.models.user import User
from src.api.deps import get_current_user, get_db
from src.config.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from src.services.token_service import TokenService
from datetime import timedelta
 
router = APIRouter()
 
# In-memory storage for test user password
test_user_password = "Bhavithak1$"
 
# In-memory storage for forgot password sessions
forgot_password_sessions = {}
 
@router.post("/login", response_model=LoginResponse, tags=["Authentication"], summary="User Login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    from datetime import datetime
   
    user = db.query(User).filter(User.email == request.email).first()
   
    if not user:
        print(f"User not found for email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
   
 
   
    print(f"User found: {user.email}, checking password...")
    if not verify_password(request.password, user.hashed_password):
        print(f"Password verification failed for user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
   
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "employee_id": user.employee_id,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name
        }
    )
   
    refresh_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "type": "refresh"
        },
        expires_delta=timedelta(days=7)
    )
   
    # Set redirect URL based on role
    role_lower = user.role.lower()
    print(f"Debug - User role: '{user.role}', role_lower: '{role_lower}'")
   
    if "hr executive" in role_lower:
        redirect_url = "/hr-executive-dashboard"
        print(f"Debug - Matched HR Executive, redirect_url: {redirect_url}")
    elif "hr manager" in role_lower:
        redirect_url = "/hr-manager-dashboard"
        print(f"Debug - Matched HR Manager, redirect_url: {redirect_url}")
    elif "team lead" in role_lower:
        redirect_url = "/team-lead-dashboard"
        print(f"Debug - Matched Team Lead, redirect_url: {redirect_url}")
    elif "manager" in role_lower:
        redirect_url = "/manager-dashboard"
        print(f"Debug - Matched Manager, redirect_url: {redirect_url}")
    elif "non-employee" in role_lower:
        redirect_url = "/non-employee-modal"
        print(f"Debug - Matched Non-Employee, redirect_url: {redirect_url}")
    elif "employee" in role_lower and "non-employee" not in role_lower:
        redirect_url = "/employee-dashboard"
        print(f"Debug - Matched Employee, redirect_url: {redirect_url}")
    else:
        redirect_url = "/employee-dashboard"  # Default fallback
        print(f"Debug - Default fallback, redirect_url: {redirect_url}")
   
    print(f"Debug - Final redirect_url before return: {redirect_url}")
   
    response = LoginResponse(
        user_id=str(user.id),
        employee_id=user.employee_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        access_token=access_token,
        refresh_token=refresh_token,
        redirect_url=redirect_url,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    print(f"Debug - Response redirect_url: {response.redirect_url}")
    return response
 
 
 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_scheme = HTTPBearer()

@router.put("/change-password", response_model=MessageResponse, tags=["Authentication"], summary="Change Password")
async def change_password(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from src.core.security import get_password_hash, verify_password
    import json
   
    # Parse request body manually
    try:
        body = await request.body()
        data = json.loads(body.decode('utf-8'))
        current_password = data.get('current_password')
        new_password = data.get('new_password')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request format: {str(e)}"
        )
   
    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both current_password and new_password are required"
        )
   
    # JWT Token Required: get_current_user dependency validates the Bearer token
    # User Authentication: Checks if user exists from token (handled by get_current_user)
   
    # New Password Length: Minimum 6 characters
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long"
        )
   
    # Current Password Verification: Must provide correct current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
   
    # Password Uniqueness: New password cannot be same as current
    if verify_password(new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as current password"
        )
   
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
   
    return MessageResponse(message="Password changed successfully")
 
 
@router.post("/forgot-password", response_model=MessageResponse, tags=["Authentication"], summary="Forgot Password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    print(f"Forgot password request for: {request.email}")
   
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return MessageResponse(message="If the email exists, an OTP has been sent")
   
    success = TokenService.create_and_send_otp(db, request.email)
    print(f"OTP creation success: {success}")
   
    if success:
        # Store email in session for later use
        forgot_password_sessions["current_reset_email"] = request.email
        return MessageResponse(message="OTP sent to your email")
    else:
        return MessageResponse(message="Failed to send OTP")
 
@router.post("/resend-otp", response_model=MessageResponse, tags=["Authentication"], summary="Resend OTP")
def resend_otp(request: ResendOtpRequest, db: Session = Depends(get_db)):
    success = TokenService.create_and_send_otp(db, request.email)
    if success:
        return MessageResponse(message="OTP resent to your email")
    else:
        return MessageResponse(message="If the email exists, an OTP has been sent")
 
@router.post("/verify-otp", response_model=MessageResponse, tags=["Authentication"], summary="Verify OTP")
def verify_otp(request: VerifyOtpRequest, db: Session = Depends(get_db)):
    # Simple OTP verification (accepts any 6-digit OTP)
    if len(request.otp) == 6 and request.otp.isdigit():
        return MessageResponse(message="OTP verified successfully")
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP format")
 
@router.post("/reset-password", response_model=MessageResponse, tags=["Authentication"], summary="Reset Password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    from src.core.security import get_password_hash
   
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirm password do not match")
   
    # Find user by email from request
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
   
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
   
    return MessageResponse(message="Password reset successfully")
 
@router.post("/logout", response_model=MessageResponse, tags=["Authentication"], summary="Logout")
def logout():
    return MessageResponse(message="Logged out successfully")
