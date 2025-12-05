from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str = "your-secret-key"
    
    class Config:
        env_file = ".env"

settings = Settings()