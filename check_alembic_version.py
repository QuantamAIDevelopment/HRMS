from sqlalchemy import create_engine, text
from src.config.settings import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text('SELECT version_num FROM alembic_version'))
    current_version = result.fetchone()
    print(f"Current alembic version: {current_version[0] if current_version else 'None'}")