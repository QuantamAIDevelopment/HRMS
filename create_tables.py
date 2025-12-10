from sqlalchemy import create_engine
from src.models.base import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(bind=engine)
print("All tables created successfully!")