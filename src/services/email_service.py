import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None):
        """Send email to recipient"""
        try:
            if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
                logger.error(f"Email service not configured. Missing SMTP settings. Cannot send email to {to_email}")
                print(f"EMAIL ERROR: SMTP not configured - server:{self.smtp_server}, port:{self.smtp_port}, user:{self.smtp_username}, pass:{'***' if self.smtp_password else 'None'}")
                return False
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            
            # Attach plain text body
            msg.attach(MIMEText(body, "plain"))
            
            # Attach HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            print(f"EMAIL SUCCESS: Sent to {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            print(f"EMAIL ERROR: Failed to send to {to_email} - {str(e)}")
            return False
    
    def send_welcome_email(self, to_email: str, full_name: str):
        """Send welcome email to new employee"""
        subject = "Welcome to HRMS"
        body = f"Welcome {full_name}! Your account has been created in the HRMS system."
        html_body = f"<html><body><h1>Welcome {full_name}!</h1><p>Your account has been created in the HRMS system.</p></body></html>"
        return self.send_email(to_email, subject, body, html_body)
    
    def send_password_reset_email(self, to_email: str, reset_token: str):
        """Send password reset email"""
        reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"
        subject = "Password Reset Request"
        body = f"Click the link below to reset your password:\n{reset_link}"
        html_body = f"<html><body><h1>Password Reset</h1><p><a href='{reset_link}'>Click here to reset your password</a></p></body></html>"
        return self.send_email(to_email, subject, body, html_body)
    
    def send_otp_email(self, to_email: str, otp: str):
        """Send OTP email"""
        subject = "Your OTP Code"
        body = f"Your OTP code is: {otp}"
        html_body = f"<html><body><h1>OTP Code</h1><p>Your OTP code is: <strong>{otp}</strong></p></body></html>"
        return self.send_email(to_email, subject, body, html_body)
    
    def send_user_credentials_email(self, to_email: str, employee_id: str, password: str, full_name: str = None, official_email: str = None):
        """Send user credentials email to new employee"""
        subject = "Your HRMS Account Credentials"
        login_email = official_email or employee_id
        body = f"Hello {full_name or 'Employee'},\n\nYour HRMS account has been created.\n\nLogin Email: {login_email}\nTemporary Password: {password}\n\nPlease login and change your password.\n\nLogin URL: {settings.frontend_url}/login"
        html_body = f"<html><body><h1>Welcome to HRMS!</h1><p>Hello {full_name or 'Employee'},</p><p>Your HRMS account has been created.</p><p><strong>Login Email:</strong> {login_email}<br><strong>Temporary Password:</strong> {password}</p><p>Please <a href='{settings.frontend_url}/login'>login</a> and change your password.</p></body></html>"
        return self.send_email(to_email, subject, body, html_body)

email_service = EmailService()

def send_user_credentials_email(to_email: str, employee_id: str, password: str, full_name: str = None, official_email: str = None):
    """Helper function to send user credentials email"""
    return email_service.send_user_credentials_email(to_email, employee_id, password, full_name, official_email)
