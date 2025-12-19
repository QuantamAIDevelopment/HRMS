from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str  # Required - must be provided via env var
    secret_key: str  # Required - must be provided via env var
    
    @property
    def sync_database_url(self) -> str:
        """Convert async database URL to sync for migrations"""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg://", "postgresql://")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    reset_token_expire_minutes: int = 15
    debug: bool = False
    host: str = "0.0.0.0"  # AKS: bind to all interfaces
    port: int = 8000  # AKS: standard port
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = ""
    dev_mode: bool = False  # Should be False in production
    frontend_url: str = "http://localhost:3000"  # Default for local dev; override in production
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()