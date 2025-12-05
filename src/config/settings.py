from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:psycho539@localhost:5432/hrms_db"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9000
    
    class Config:
        env_file = ".env"

settings = Settings()