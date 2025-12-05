from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from src.core.deps import get_db
from src.models.onboarding_process import OnboardingProcess
from src.models.user import User
import os
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, List
import json

router = APIRouter()

def generate_temp_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

def send_onboarding_email(personal_email: str, temp_password: str, name: str):
    subject = "Welcome - Your Login Credentials"
    body = f"""Dear {name},

Welcome! Your login credentials:

Email: {personal_email}
Temporary Password: {temp_password}

Valid for 24 hours. Please login and change password.

HR Team"""
    
    try:
        msg = MIMEMultipart()
        msg['From'] = "hr@company.com"
        msg['To'] = personal_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        return True
    except:
        return False

@router.post("/complete-onboarding")
async def complete_onboarding(
    email: str = Form(...),

    assets: UploadFile = File(...),
    aadhaar_file: UploadFile = File(...),
    pan_file: UploadFile = File(...),
    other_documents: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    # Get employee from OnboardingProcess by employee_id
    employee = db.query(OnboardingProcess).filter(OnboardingProcess.employee_id == email).first()
    
    # Get user email from Users table
    user = db.query(User).filter(User.employee_id == email).first()
    user_email = user.email if user else email
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save files to uploads directory only
    file_paths = {}
    required_files = {"assets": assets, "aadhaar_file": aadhaar_file, "pan_file": pan_file}
    
    for field_name, file in required_files.items():
        file_path = os.path.join(upload_dir, f"{email}_{field_name}_{file.filename}")
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        file_paths[field_name] = file_path
    
    # Save optional other documents
    other_doc_paths = []
    if other_documents:
        for i, doc in enumerate(other_documents):
            file_path = os.path.join(upload_dir, f"{email}_other_doc_{i}_{doc.filename}")
            with open(file_path, "wb") as buffer:
                content = await doc.read()
                buffer.write(content)
            other_doc_paths.append(file_path)
    
    temp_password = generate_temp_password()
    employee.status = "Completed"
    
    db.commit()
    
    send_onboarding_email(user_email, temp_password, employee.name)
    
    return {
        "message": "Onboarding completed and email sent", 
        "employee_id": employee.employee_id,
        "annual_ctc": float(employee.annual_ctc),
        "email_sent_to": user_email,
        "files_uploaded": {
            "assets": file_paths.get("assets"),
            "aadhaar_file": file_paths.get("aadhaar_file"),
            "pan_file": file_paths.get("pan_file"),
            "other_documents": other_doc_paths
        }
    }