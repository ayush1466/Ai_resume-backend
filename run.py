"""
Application entry point
Run this file to start the server: python run.py
"""
from openai import api_key
import uvicorn
from app.core.config import settings
from app.core.logging import logger
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    """Start the application server"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    api_key = os.getenv('GROK_API_KEY')
    print(f"API Key loaded: {api_key[:10] if api_key else 'None'}...")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()