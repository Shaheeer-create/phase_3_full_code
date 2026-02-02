"""
Application configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    database_url: str
    better_auth_secret: str
    cors_origins: str = "http://localhost:3000"
    host: str = "0.0.0.0"
    port: int = 8000

    # Gemini Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash-exp"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 2048

    # Usage Limits
    max_messages_per_day: int = 100
    max_tokens_per_month: int = 500000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
