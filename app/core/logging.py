"""
Centralized logging configuration
"""
import logging
import sys
from typing import Any
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """
    Configure and return application logger
    """
    # Create logger
    logger = logging.getLogger("resume_analyzer")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Create formatter
    if settings.LOG_FORMAT == "json":
        # JSON format for production
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
        )
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Create global logger instance
logger = setup_logging()


def log_request(method: str, path: str, status_code: int, duration: float):
    """Log HTTP request details"""
    logger.info(
        f"Request: {method} {path} - Status: {status_code} - Duration: {duration:.3f}s"
    )


def log_error(error: Exception, context: str = ""):
    """Log error with context"""
    logger.error(f"Error in {context}: {type(error).__name__} - {str(error)}")


def log_service_call(service: str, action: str, details: Any = None):
    """Log service layer calls"""
    message = f"Service: {service} - Action: {action}"
    if details:
        message += f" - Details: {details}"
    logger.info(message)