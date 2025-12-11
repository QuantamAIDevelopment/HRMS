from datetime import datetime, timedelta
from jose import jwt
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class TokenService:
    """Service for managing JWT tokens"""
    
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
    REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days
    RESET_TOKEN_EXPIRE_MINUTES = settings.reset_token_expire_minutes
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        """Create a new access token"""
        to_encode = data.copy()
        now = datetime.utcnow()
        
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=TokenService.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": now})
        encoded_jwt = jwt.encode(to_encode, TokenService.SECRET_KEY, algorithm=TokenService.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a new refresh token"""
        to_encode = data.copy()
        now = datetime.utcnow()
        expire = now + timedelta(days=TokenService.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "iat": now, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, TokenService.SECRET_KEY, algorithm=TokenService.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_reset_token(data: dict) -> str:
        """Create a password reset token"""
        to_encode = data.copy()
        now = datetime.utcnow()
        expire = now + timedelta(minutes=TokenService.RESET_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": now, "type": "reset"})
        encoded_jwt = jwt.encode(to_encode, TokenService.SECRET_KEY, algorithm=TokenService.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode a token"""
        try:
            payload = jwt.decode(token, TokenService.SECRET_KEY, algorithms=[TokenService.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise ValueError("Token has expired")
        except jwt.JWTError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise ValueError("Invalid token")
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """Generate new access token from refresh token"""
        try:
            payload = TokenService.verify_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise ValueError("Invalid refresh token")
            
            user_id = payload.get("sub")
            new_access_token = TokenService.create_access_token({"sub": user_id})
            return new_access_token
        
        except Exception as e:
            logger.error(f"Failed to refresh token: {str(e)}")
            raise
    
    @staticmethod
    def decode_reset_token(reset_token: str) -> str:
        """Decode reset token and return email"""
        try:
            payload = TokenService.verify_token(reset_token)
            
            if payload.get("type") != "reset":
                raise ValueError("Invalid reset token")
            
            return payload.get("email")
        
        except Exception as e:
            logger.error(f"Failed to decode reset token: {str(e)}")
            raise
    
    @staticmethod
    def create_and_send_otp(db, email: str) -> bool:
        """Create and send OTP to email"""
        try:
            # Generate 6-digit OTP
            import random
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            logger.info(f"Generated OTP for {email}: {otp}")
            
            # Send OTP via email service
            from services.email_service import email_service
            email_sent = email_service.send_otp_email(email, otp)
            
            if email_sent:
                logger.info(f"OTP email sent successfully to {email}")
                return True
            else:
                logger.error(f"Failed to send OTP email to {email}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create and send OTP: {str(e)}")
            return False

token_service = TokenService()
