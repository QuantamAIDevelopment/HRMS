from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import logging

DATABASE_URL = "postgresql://postgres:Bhavitha1$@localhost/Hrms-backend"

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
