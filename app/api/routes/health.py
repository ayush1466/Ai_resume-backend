"""
Health check endpoints
"""
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.response import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/", response_model=HealthResponse)
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        HealthResponse with application status
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT
    )