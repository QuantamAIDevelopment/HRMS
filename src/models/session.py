from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Use sync database URL for synchronous API endpoints
sync_database_url = settings.sync_database_url
engine = create_engine(sync_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

