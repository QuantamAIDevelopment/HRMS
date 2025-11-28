from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    refresh_token_expire_days: int = 7
    reset_token_expire_minutes: int = 15
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    from_email: str
    dev_mode: bool = True
    frontend_url: str
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()