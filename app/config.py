"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "Resume Analyzer API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API settings
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    
    # CORS settings
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Groq API settings
    GROQ_API_KEY: str
    GROQ_API_BASE: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 2000
    
    # File upload settings
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = ".pdf"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'


# Create settings instance
settings = Settings()