from src.models.base import Base
from src.models.session import engine
from src.models import *  # Import all models

# Create all tables (will skip existing ones)
Base.metadata.create_all(bind=engine)
print("All tables created successfully!")