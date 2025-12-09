from pydantic_settings import BaseSettings
from typing import Optional
from urllib.parse import quote_plus
from pydantic import computed_field

class Settings(BaseSettings):
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "Panda@123"
    POSTGRES_DB: str = "HRMS-Backend"
    SECRET_KEY: str = "your-secret-key-here"
    ENV: str = "development"
    debug: bool = True
    
    @computed_field
    @property
    def database_url(self) -> str:
        password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"

settings = Settings()