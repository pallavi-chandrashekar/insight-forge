from pydantic_settings import BaseSettings
from typing import List, Union
from functools import lru_cache
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "InsightForge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./insightforge.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Security
    SECRET_KEY: str = "insightforge-default-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: Union[List[str], str] = "http://localhost:3000,http://localhost:5173"

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 100  # MB

    # LLM (Optional - users provide their own keys)
    API_KEY: str = ""  # Legacy - kept for backward compatibility
    LLM_MODEL: str = "claude-sonnet-4-20250514"
    LLM_MAX_TOKENS: int = 4096

    # Free tier fallback (Google Gemini)
    GEMINI_FREE_API_KEY: str = "AIzaSyAT2k1WZsx7qWo039jlm2R6eZ8CgN7FxkE"  # Free tier Gemini API key
    GEMINI_FREE_MODEL: str = "gemini-1.5-flash"  # Fast, free model

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Tableau
    TABLEAU_PUBLIC_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
