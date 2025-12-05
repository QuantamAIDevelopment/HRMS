from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter(tags=["OTP"])

class OtpOnlyRequest(BaseModel):
    otp: str

class PasswordResetRequest(BaseModel):
    email: EmailStr
    new_password: str
    confirm_password: str

class MessageResponse(BaseModel):
    message: str
    success: bool = True

@router.post("/verify-otp-only", response_model=MessageResponse)
def verify_otp_only(request: OtpOnlyRequest):
    if len(request.otp) == 6 and request.otp.isdigit():
        return MessageResponse(message="OTP verified successfully")
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP format")

@router.post("/reset-password-only", response_model=MessageResponse)
def reset_password_only(request: PasswordResetRequest):
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    return MessageResponse(message="Password reset successfully")