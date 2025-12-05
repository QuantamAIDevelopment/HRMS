from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.deps import get_db
from src.models.temp_credentials import TempCredentials
from src.schemas.onboarding_email import OnboardingEmailRequest, OnboardingEmailResponse
from src.services.onboarding_email_service import generate_temp_password, send_onboarding_email
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/send-onboarding-email", response_model=OnboardingEmailResponse)
async def send_onboarding_email_api(
    request: OnboardingEmailRequest,
    db: Session = Depends(get_db)
):
    temp_password = generate_temp_password()
    expires_at = datetime.now() + timedelta(days=1)
    
    # Store temp credentials
    temp_cred = TempCredentials(
        official_email=request.official_email,
        temp_password=temp_password,
        expires_at=expires_at
    )
    
    db.add(temp_cred)
    db.commit()
    
    # Send email
    email_sent = send_onboarding_email(
        request.personal_email,
        request.official_email,
        temp_password,
        request.employee_name
    )
    
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send email")
    
    return OnboardingEmailResponse(
        message="Onboarding email sent successfully",
        official_email=request.official_email
    )