from pydantic import BaseModel, EmailStr

class OnboardingEmailRequest(BaseModel):
    personal_email: EmailStr
    official_email: EmailStr
    employee_name: str

class OnboardingEmailResponse(BaseModel):
    message: str
    official_email: str