"""
PDF text extraction service
"""
import io
from typing import BinaryIO
import PyPDF2
from app.core.logging import logger, log_service_call, log_error
from app.exceptions import PDFExtractionError
from app.utils.helpers import clean_text


class PDFService:
    """Service for handling PDF operations"""
    
    @staticmethod
    async def extract_text_from_pdf(pdf_content: bytes) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Extracted text
            
        Raises:
            PDFExtractionError: If extraction fails
        """
        log_service_call("PDFService", "extract_text_from_pdf", f"{len(pdf_content)} bytes")
        
        try:
            # Create PDF reader from bytes
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                raise PDFExtractionError(
                    "PDF is encrypted",
                    details="Cannot extract text from encrypted PDFs"
                )
            
            # Get number of pages
            num_pages = len(pdf_reader.pages)
            logger.info(f"PDF has {num_pages} pages")
            
            if num_pages == 0:
                raise PDFExtractionError(
                    "PDF has no pages",
                    details="The PDF file appears to be empty"
                )
            
            # Extract text from all pages
            text_parts = []
            for page_num in range(num_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
                    continue
            
            # Combine all text
            full_text = "\n".join(text_parts)
            
            # Clean the text
            full_text = clean_text(full_text)
            
            # Validate extracted text
            if not full_text or len(full_text.strip()) < 50:
                raise PDFExtractionError(
                    "Insufficient text extracted from PDF",
                    details="The PDF might be scanned or image-based. Try using a text-based PDF."
                )
            
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            return full_text
            
        except PyPDF2.errors.PdfReadError as e:
            log_error(e, "PDF reading")
            raise PDFExtractionError(
                "Failed to read PDF file",
                details="The file might be corrupted or not a valid PDF"
            )
        except PDFExtractionError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            log_error(e, "PDF extraction")
            raise PDFExtractionError(
                "Unexpected error during PDF extraction",
                details=str(e)
            )


# Create global instance
pdf_service = PDFService()