from fastapi import Depends
from sqlalchemy.orm import Session
from src.models.session import get_db
from src.core.security import get_current_user_email
from src.models.user import User

def get_current_user(db: Session = Depends(get_db), email: str = Depends(get_current_user_email)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user