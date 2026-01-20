"""
Input validation utilities
"""
from fastapi import UploadFile
from app.core.config import settings
from app.core.logging import logger
from app.exceptions import FileValidationError


async def validate_pdf_file(file: UploadFile) -> None:
    """
    Validate uploaded PDF file
    
    Args:
        file: Uploaded file object
        
    Raises:
        FileValidationError: If validation fails
    """
    # Check if file exists
    if not file:
        raise FileValidationError("No file provided")
    
    # Check filename
    if not file.filename:
        raise FileValidationError("File has no filename")
    
    # Check file type
    file_extension = f".{file.filename.split('.')[-1].lower()}"
    if file_extension not in settings.allowed_file_types_list:
        raise FileValidationError(
            f"Invalid file type. Allowed types: {', '.join(settings.allowed_file_types_list)}",
            details=f"Received: {file_extension}"
        )
    
    # Read file to check size
    content = await file.read()
    file_size = len(content)
    
    # Reset file pointer for later reading
    await file.seek(0)
    
    # Check file size
    if file_size == 0:
        raise FileValidationError("File is empty")
    
    if file_size > settings.max_file_size_bytes:
        raise FileValidationError(
            f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB",
            details=f"File size: {file_size / (1024*1024):.2f}MB"
        )
    
    logger.info(f"File validation passed: {file.filename} ({file_size / 1024:.2f}KB)")


def validate_job_description(job_description: str) -> str:
    """
    Validate and clean job description
    
    Args:
        job_description: Raw job description text
        
    Returns:
        Cleaned job description
    """
    # Convert to string if needed
    if not isinstance(job_description, str):
        job_description = str(job_description)
    
    # Strip whitespace
    job_description = job_description.strip()
    
    # Limit length (optional)
    max_length = 10000  # 10k characters
    if len(job_description) > max_length:
        logger.warning(f"Job description truncated from {len(job_description)} to {max_length} characters")
        job_description = job_description[:max_length]
    
    return job_description