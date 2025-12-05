import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str):
    try:
        print(f"SMTP Config: {settings.smtp_server}:{settings.smtp_port}")
        print(f"From: {settings.from_email} To: {to_email}")
        
        msg = MIMEMultipart()
        msg['From'] = settings.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        print("Starting TLS...")
        server.starttls()
        print("Logging in...")
        server.login(settings.smtp_username, settings.smtp_password)
        
        text = msg.as_string()
        print("Sending email...")
        server.sendmail(settings.from_email, to_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        print(f"SUCCESS: Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        print(f"ERROR: Email sending failed - {type(e).__name__}: {e}")
        return False

def send_otp_email(email: str, otp: str):
    subject = "Your OTP for Password Reset"
    body = f"""Dear User,

Your OTP for password reset is: {otp}

This OTP is valid for 10 minutes only.

If you did not request this, please ignore this email.

Best regards,
HRMS Team"""
    
    print(f"Attempting to send OTP {otp} to {email}")
    result = send_email(email, subject, body)
    print(f"Email send result: {result}")
    return result

def send_password_reset_email(email: str, reset_token: str):
    subject = "Password Reset Request"
    body = f"""Dear User,

You have requested a password reset. Your reset token is: {reset_token}

Best regards,
HRMS Team"""
    
    return send_email(email, subject, body)

def send_welcome_email(email: str):
    subject = "Welcome to HRMS"
    body = "Welcome to our HRMS system!"
    return send_email(email, subject, body)

def send_user_credentials_email(email: str, password: str):
    subject = "Your HRMS Account Credentials - Valid for 24 Hours"
    body = f"""Dear User,

Your HRMS account has been created successfully.

Your login credentials are:
Mail ID: {email}
Temporary Password: {password}

IMPORTANT: This temporary password is valid for 24 hours only.
Please login and change your password within 24 hours.

If you don't change your password within 24 hours, you will need to contact your administrator for a new temporary password.

Best regards,
HRMS Team"""
    
    return send_email(email, subject, body)

def send_payslip_email(email: str):
    subject = "Your Payslip"
    body = "Please find your payslip attached."
    return send_email(email, subject, body)