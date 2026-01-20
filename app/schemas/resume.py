"""
Pydantic models for resume analysis
"""
from typing import List
from pydantic import BaseModel, Field, validator


class AnalysisResult(BaseModel):
    """
    Resume analysis result model
    
    This is returned from the /api/analyze endpoint
    """
    atsScore: int = Field(
        ...,
        ge=0,
        le=100,
        description="ATS compatibility score (0-100)"
    )
    strengths: List[str] = Field(
        ...,
        min_items=1,
        description="List of resume strengths"
    )
    improvements: List[str] = Field(
        ...,
        min_items=1,
        description="List of areas for improvement"
    )
    missingKeywords: List[str] = Field(
        ...,
        description="List of missing important keywords"
    )
    suggestions: List[str] = Field(
        ...,
        min_items=1,
        description="List of actionable suggestions"
    )
    
    @validator("atsScore")
    def validate_ats_score(cls, v):
        """Ensure ATS score is within valid range"""
        if not 0 <= v <= 100:
            raise ValueError("ATS score must be between 0 and 100")
        return v
    
    @validator("strengths", "improvements", "suggestions")
    def validate_non_empty_list(cls, v):
        """Ensure lists are not empty"""
        if not v:
            raise ValueError("List cannot be empty")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "atsScore": 75,
                "strengths": [
                    "Clear and concise professional summary",
                    "Quantified achievements with metrics",
                    "Well-structured work experience"
                ],
                "improvements": [
                    "Add more technical skills",
                    "Include certifications",
                    "Optimize section headers for ATS"
                ],
                "missingKeywords": [
                    "Project Management",
                    "Agile Methodology",
                    "Data Analysis"
                ],
                "suggestions": [
                    "Use consistent action verbs",
                    "Add a technical skills section",
                    "Include portfolio links"
                ]
            }
        }