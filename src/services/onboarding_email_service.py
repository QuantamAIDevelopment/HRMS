import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import string
from datetime import datetime, timedelta

def generate_temp_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def send_onboarding_email(personal_email: str, official_email: str, temp_password: str, employee_name: str):
    subject = "Welcome to Company - Your Login Credentials"
    
    body = f"""
    Dear {employee_name},

    Welcome to our company! Your official email and temporary login credentials are:

    Official Email: {official_email}
    Temporary Password: {temp_password}

    This password is valid for 24 hours only. Please login and change your password.

    Best regards,
    HR Team
    """
    
    # Configure your SMTP settings here
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "your-email@company.com"
    sender_password = "your-app-password"
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = personal_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False