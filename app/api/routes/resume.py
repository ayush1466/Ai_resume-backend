"""
Resume analysis endpoints
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.core.logging import logger
from app.schemas.resume import AnalysisResult
from app.schemas.response import ErrorResponse
from app.utils.validators import validate_pdf_file, validate_job_description
from app.services.analysis_service import analysis_service
from app.exceptions import (
    FileValidationError,
    PDFExtractionError,
    GroqAPIError,
    AnalysisError
)

router = APIRouter(prefix="/api", tags=["Resume Analysis"])


@router.post(
    "/analyze",
    response_model=AnalysisResult,
    responses={
        400: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Server Error"}
    }
)
async def analyze_resume(
    resume: UploadFile = File(..., description="Resume PDF file"),
    jobDescription: str = Form("", description="Optional job description for targeted analysis")
):
    """
    Analyze resume and provide feedback
    """
    try:
        # Step 1: Validate file
        logger.info(f"Received resume analysis request: {resume.filename}")
        await validate_pdf_file(resume)

        # Step 2: Validate job description
        job_desc = validate_job_description(jobDescription)

        # Step 3: Read PDF bytes
        pdf_content = await resume.read()

        # Step 4: Full analysis (includes resume validation internally)
        result = await analysis_service.analyze_resume(
            pdf_content=pdf_content,
            job_description=job_desc if job_desc else None
        )

        logger.info(
            f"Analysis completed for {resume.filename} - ATS Score: {result.atsScore}"
        )
        return result

    except FileValidationError as e:
        logger.warning(f"File validation failed: {e.message}")
        raise HTTPException(
            status_code=400,
            detail={"error": e.message, "details": e.details}
        )

    except PDFExtractionError as e:
        logger.error(f"PDF extraction failed: {e.message}")
        raise HTTPException(
            status_code=400,
            detail={"error": e.message, "details": e.details}
        )

    except AnalysisError as e:
        logger.warning(f"Analysis rejected: {e.message}")
        raise HTTPException(
            status_code=400,
            detail={"error": e.message, "details": e.details}
        )

    except GroqAPIError as e:
        logger.error(f"Groq API error: {e.message}")
        raise HTTPException(
            status_code=500,
            detail={"error": "AI analysis failed", "details": e.details}
        )

    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "details": "An unexpected error occurred during analysis"
            }
        )
