"""
PDF Report Download Endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.core.logging import logger
from app.schemas.resume import AnalysisResult
from app.services.pdf_report_service import pdf_report_service
from app.exceptions import AnalysisError

router = APIRouter(prefix="/api", tags=["Reports"])


@router.post("/download-report")
async def download_report(analysis_result: AnalysisResult):
    """
    Generate and download PDF report from analysis results
    
    Args:
        analysis_result: AnalysisResult object (sent in request body)
        
    Returns:
        PDF file as downloadable attachment
    """
    try:
        logger.info(f"Generating PDF report for ATS score: {analysis_result.atsScore}")
        
        # Generate PDF report
        pdf_buffer = pdf_report_service.generate_report(
            analysis_result=analysis_result
        )
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Resume_Analysis_Report_{timestamp}.pdf"
        
        logger.info(f"PDF report generated successfully: {filename}")
        
        # Return as downloadable file
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to generate PDF report: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to generate PDF report",
                "details": str(e)
            }
        )