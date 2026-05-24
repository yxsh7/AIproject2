"""Application configuration"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "DevMetrics AI"
    DEBUG: bool = False
    VERSION: str = "0.1.0"
    DEMO_MODE: bool = False

    # Database
    DATABASE_URL: str
    TEST_DATABASE_URL: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI APIs
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "openrouter/hunter-alpha"

    # AI Model Configuration (for cost control)
    AI_MODEL_PROVIDER: str = "openrouter"  # "openrouter", "openai", or "anthropic"
    AI_MODEL_NAME: str = "openrouter/hunter-alpha"
    AI_MODEL_TEMPERATURE: float = 0.1
    AI_MODEL_MAX_TOKENS: int = 1024
    OPENAI_API_BASE: str = ""  # Optional: for OpenRouter or other OpenAI-compatible APIs

    # GitHub Integration
    GITHUB_APP_ID: str = ""
    GITHUB_APP_SECRET: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""

    # Jira Integration
    JIRA_API_TOKEN: str = ""
    JIRA_WORKSPACE_URL: str = ""

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
