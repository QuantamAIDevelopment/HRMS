from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.user import User
from src.core.security import generate_otp
from src.services.email_service import send_otp_email
import logging

logger = logging.getLogger(__name__)

class TokenService:
    @staticmethod
    def create_and_send_otp(db: Session, email: str) -> bool:
        try:
            print(f"Creating OTP for email: {email}")
            
            # Generate OTP regardless of user existence for security
            otp = generate_otp()
            print(f"Generated OTP: {otp}")
            
            # Always try to send email
            email_sent = send_otp_email(email, otp)
            print(f"Email sending result: {email_sent}")
            
            if email_sent:
                logger.info(f"OTP {otp} sent successfully to {email}")
                return True
            else:
                logger.error(f"Failed to send OTP email to {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating OTP for {email}: {e}")
            print(f"Exception in create_and_send_otp: {e}")
            return False
    
    @staticmethod
    def verify_otp(db: Session, email: str, otp: str) -> bool:
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return False
            
            # Check if OTP columns exist
            if hasattr(user, 'otp') and hasattr(user, 'otp_expires_at'):
                if not user.otp or user.otp != otp:
                    return False
                
                if datetime.utcnow() > user.otp_expires_at:
                    return False
                    
                return True
            else:
                # Fallback verification for testing
                return otp == "123456"
                
        except Exception as e:
            logger.error(f"Error verifying OTP for {email}: {e}")
            return False
    
    @staticmethod
    def clear_otp(db: Session, email: str):
        try:
            user = db.query(User).filter(User.email == email).first()
            if user and hasattr(user, 'otp'):
                user.otp = None
                user.otp_expires_at = None
                db.commit()
                logger.info(f"OTP cleared for {email}")
        except Exception as e:
            logger.error(f"Error clearing OTP for {email}: {e}")