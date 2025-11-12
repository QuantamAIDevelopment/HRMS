from ..models.session import SessionLocal
from ..models.user import User
from ..core.security import get_password_hash

def seed_admin_user():
    db = SessionLocal()
    admin = User(
        email="admin@hrms.com",
        hashed_password=get_password_hash("admin123")
    )
    db.add(admin)
    db.commit()
    db.close()