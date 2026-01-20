"""
Standard API response models
"""
from typing import Any, Optional
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {}
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "Validation Error",
                "detail": "File type not supported"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "production"
            }
        }