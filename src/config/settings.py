from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    reset_token_expire_minutes: int = 15
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 9000
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = ""
    dev_mode: bool = True
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()