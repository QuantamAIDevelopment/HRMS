from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")
    
    APP_NAME: str = "HRMS Backend API"
    DEBUG: bool = True
    database_url: str = "postgresql://postgres:bhavani%40123@127.0.0.1:5432/hrms_app"
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30

settings = Settings()