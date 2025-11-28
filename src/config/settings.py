from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "HRMS_Backend"
    SECRET_KEY: str = "your-secret-key-here"
    ENV: str = "development"
    database_url: str = "postgresql://postgres:Panda%40123@127.0.0.1:5432/HRMS-Backend"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"

settings = Settings()