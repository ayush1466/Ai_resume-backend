"""
Resume analysis orchestration service
Coordinates PDF extraction and AI analysis
"""
from typing import Optional
from app.core.logging import logger, log_service_call
from app.exceptions import AnalysisError
from app.schemas.resume import AnalysisResult
from app.services.pdf_service import pdf_service
from app.services.groq_service import groq_service


class AnalysisService:
    """
    Orchestrates the complete resume analysis process
    Combines PDF extraction and AI analysis
    """
    
    async def analyze_resume(
        self,
        pdf_content: bytes,
        job_description: Optional[str] = None
    ) -> AnalysisResult:
        """
        Complete resume analysis workflow
        
        Args:
            pdf_content: PDF file content as bytes
            job_description: Optional job description for targeted analysis
            
        Returns:
            AnalysisResult with complete analysis
            
        Raises:
            AnalysisError: If analysis fails at any step
        """
        log_service_call(
            "AnalysisService",
            "analyze_resume",
            f"PDF: {len(pdf_content)} bytes, Job desc: {bool(job_description)}"
        )
        
        try:
            # Step 1: Extract text from PDF
            logger.info("Step 1/2: Extracting text from PDF...")
            resume_text = await pdf_service.extract_text_from_pdf(pdf_content)
            
            if not resume_text:
                raise AnalysisError(
                    "No text extracted from PDF",
                    details="The PDF might be empty or image-based"
                )
            
            logger.info(f"Successfully extracted {len(resume_text)} characters")
            
            # Step 2: Analyze with Groq
            logger.info("Step 2/2: Analyzing resume with AI...")
            analysis_result = await groq_service.analyze_resume(
                resume_text=resume_text,
                job_description=job_description or ""
            )
            
            logger.info("Resume analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Analysis failed: {type(e).__name__} - {str(e)}")
            
            # Re-raise specific errors
            if isinstance(e, (AnalysisError, Exception)):
                raise
            
            # Wrap unexpected errors
            raise AnalysisError(
                "Unexpected error during analysis",
                details=str(e)
            )


# Create global instance
analysis_service = AnalysisService()