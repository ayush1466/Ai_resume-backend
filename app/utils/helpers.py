"""
General helper functions
"""
import re
from typing import Dict, Any


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = text.replace('\x00', '')  # Null bytes
    text = text.replace('\r\n', '\n')  # Normalize line endings
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def extract_keywords(text: str, min_length: int = 3) -> list:
    """
    Extract potential keywords from text
    
    Args:
        text: Input text
        min_length: Minimum keyword length
        
    Returns:
        List of keywords
    """
    # Convert to lowercase
    text = text.lower()
    
    # Split into words
    words = re.findall(r'\b\w+\b', text)
    
    # Filter by length and remove duplicates
    keywords = list(set([
        word for word in words 
        if len(word) >= min_length
    ]))
    
    return keywords


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def sanitize_json_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize JSON response to ensure it's valid
    
    Args:
        data: Dictionary to sanitize
        
    Returns:
        Sanitized dictionary
    """
    if not isinstance(data, dict):
        return {}
    
    # Remove None values
    sanitized = {k: v for k, v in data.items() if v is not None}
    
    # Ensure lists are not None
    for key, value in sanitized.items():
        if isinstance(value, list) and value is None:
            sanitized[key] = []
    
    return sanitized