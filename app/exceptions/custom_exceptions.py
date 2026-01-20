"""
Custom exception classes for the application
"""


class ResumeAnalyzerError(Exception):
    """Base exception for all application errors"""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class PDFExtractionError(ResumeAnalyzerError):
    """
    Raised when PDF text extraction fails
    
    Examples:
        - Corrupted PDF file
        - Scanned PDF without OCR
        - Invalid PDF format
    """
    pass


class GroqAPIError(ResumeAnalyzerError):
    """
    Raised when Groq API call fails
    
    Examples:
        - Invalid API key
        - Rate limit exceeded
        - API timeout
        - Invalid response format
    """
    pass


class FileValidationError(ResumeAnalyzerError):
    """
    Raised when uploaded file validation fails
    
    Examples:
        - File too large
        - Invalid file type
        - Empty file
    """
    pass


class AnalysisError(ResumeAnalyzerError):
    """
    Raised when resume analysis process fails
    
    Examples:
        - Missing required data
        - Analysis parsing error
        - Unexpected service error
    """
    pass


class ConfigurationError(ResumeAnalyzerError):
    """
    Raised when application configuration is invalid
    
    Examples:
        - Missing environment variables
        - Invalid configuration values
    """
    pass