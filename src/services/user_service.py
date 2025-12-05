from sqlalchemy.orm import Session
from src.models.user import User
from src.core.security import get_password_hash, verify_password
from src.schemas.user import UserCreate
from src.services.email_service import send_user_credentials_email
from datetime import datetime, timedelta
import secrets
import string

class UserService:
    @staticmethod
    def generate_temp_password(length=8):
        """Generate a random temporary password"""
        characters = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    @staticmethod
    def create_user_with_temp_password(db: Session, employee_id: str, email: str, full_name: str, role: str = "EMPLOYEE"):
        """Create user with temporary password valid for 1 hour"""
        temp_password = UserService.generate_temp_password()
        hashed_password = get_password_hash(temp_password)
        
        # Set expiry to 1 hour from now
        expiry_time = datetime.utcnow() + timedelta(hours=1)
        
        db_user = User(
            employee_id=employee_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_temp_password=True,
            temp_password_expires_at=expiry_time
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Send email with credentials
        send_user_credentials_email(email, temp_password)
        
        return db_user, temp_password
    
    @staticmethod
    def create_user(db: Session, user: UserCreate):
        hashed_password = get_password_hash(user.password)
        db_user = User(
            employee_id=user.employee_id,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            role=user.role,
            is_temp_password=False
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = UserService.get_user_by_email(db, email)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user