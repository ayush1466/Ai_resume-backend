"""
Application configuration management using Pydantic Settings
Loads and validates environment variables from .env file
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # ───────────────────────────
    # Application Settings
    # ───────────────────────────
    APP_NAME: str = "Resume Analyzer API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # ───────────────────────────
    # Server Settings
    # ───────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 5000

    # ───────────────────────────
    # CORS Settings
    # ───────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000"


    # ───────────────────────────
    # 🔹 Groq API Settings
    # ───────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_API_BASE: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL: str = "llama3-8b-8192"
    GROQ_MAX_TOKENS: int = 2000
    GROQ_TEMPERATURE: float = 0.7

    # ───────────────────────────
    # File Upload Settings
    # ───────────────────────────
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = ".pdf"

    # ───────────────────────────
    # Logging
    # ───────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # ───────────────────────────
    # Rate Limiting
    # ───────────────────────────
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 10

    # ───────────────────────────
    # Computed Properties
    # ───────────────────────────
    @property
    def allowed_origins_list(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return [self.ALLOWED_ORIGINS]

    @property
    def allowed_file_types_list(self) -> List[str]:
        if isinstance(self.ALLOWED_FILE_TYPES, str):
            return [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(",")]
        return [self.ALLOWED_FILE_TYPES]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


# Global settings instance
settings = Settings()
