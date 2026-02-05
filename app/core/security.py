"""
Security utilities and middleware
"""
from typing import List
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_cors_middleware_config() -> dict:
    """
    Get CORS middleware configuration
    """
    # Convert comma-separated string to list
    allowed_origins = settings.ALLOWED_ORIGINS.split(",")
    
    return {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize uploaded filename to prevent path traversal attacks
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = filename.replace("/", "").replace("\\", "")
    
    # Remove dangerous characters
    dangerous_chars = ["<", ">", ":", '"', "|", "?", "*"]
    for char in dangerous_chars:
        filename = filename.replace(char, "")
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:250] + (f".{ext}" if ext else "")
    
    return filename


def validate_api_key(api_key: str) -> bool:
    """
    Validate Groq API key format
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid format
    """
    if not api_key:
        return False
    
    # Basic validation - Groq keys start with 'gsk_'
    if not api_key.startswith("gsk_"):
        return False
    
    # Minimum length check
    if len(api_key) < 20:
        return False
    
    return True


async def rate_limit_middleware(request: Request, call_next):
    """
    Simple rate limiting middleware (placeholder)
    For production, use Redis-based rate limiting
    
    Args:
        request: FastAPI request
        call_next: Next middleware/handler
        
    Returns:
        Response
    """
    # TODO: Implement proper rate limiting with Redis
    response = await call_next(request)
    return response