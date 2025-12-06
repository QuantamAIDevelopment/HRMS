from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.session import get_db
from core.security import get_current_user_email
from models.user import User

def get_current_user(db: Session = Depends(get_db), email: str = Depends(get_current_user_email)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user