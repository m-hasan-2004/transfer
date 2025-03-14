# config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "your_secret_key"  # Change this to a secure key in production
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"  # Use an .env file to keep sensitive info safe

settings = Settings()
