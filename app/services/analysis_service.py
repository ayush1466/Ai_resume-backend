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
from app.utils.resume_validator import looks_like_resume


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
        """

        log_service_call(
            "AnalysisService",
            "analyze_resume",
            f"PDF: {len(pdf_content)} bytes, Job desc: {bool(job_description)}"
        )

        try:
            # Step 1: Extract text from PDF
            logger.info("Step 1/3: Extracting text from PDF...")
            resume_text = await pdf_service.extract_text_from_pdf(pdf_content)

            if not resume_text.strip():
                raise AnalysisError(
                    "No text extracted from PDF",
                    details="The PDF might be empty or image-based"
                )

            logger.info(f"Extracted {len(resume_text)} characters")

            # 🔥 Step 2: Resume validation (IMPORTANT)
            logger.info("Step 2/3: Validating resume content...")
            if not looks_like_resume(resume_text):
                logger.warning("Uploaded document is not a resume")
                raise AnalysisError(
                    "Invalid document",
                    details="Uploaded file is not a resume. Please upload a valid resume PDF."
                )

            logger.info("Resume validation passed")

            # Step 3: Analyze with Groq
            logger.info("Step 3/3: Analyzing resume with AI...")
            analysis_result = await groq_service.analyze_resume(
                resume_text=resume_text,
                job_description=job_description or ""
            )

            logger.info("Resume analysis completed successfully")
            return analysis_result

        except AnalysisError:
            # Re-raise known analysis errors
            raise

        except Exception as e:
            logger.error(f"Analysis failed: {type(e).__name__} - {str(e)}")
            raise AnalysisError(
                "Unexpected error during analysis",
                details=str(e)
            )


# Global instance
analysis_service = AnalysisService()
