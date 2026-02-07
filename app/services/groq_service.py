"""
Groq API integration service
"""

import json
from typing import Dict, Any

from openai import OpenAI

from app.core.config import settings
from app.core.logging import logger, log_service_call, log_error
from app.exceptions import GroqAPIError
from app.schemas.resume import AnalysisResult


class GroqService:
    """Service for interacting with Groq API"""

    def __init__(self):
        """Initialize Groq API client"""
        self.client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_API_BASE
        )
        logger.info(f"Groq service initialized with model: {settings.GROQ_MODEL}")

    def _build_analysis_prompt(
        self,
        resume_text: str,
        job_description: str = ""
    ) -> str:
        """
        Build the prompt for resume analysis
        """

        job_section = ""
        keyword_note = ""
        alignment_note = ""

        if job_description:
            job_section = f"\nJob Description:\n{job_description}"
            keyword_note = " from the job description"
            alignment_note = "- Alignment with the provided job description"

        prompt = f"""
Analyze the following resume and provide detailed feedback in JSON format.

Resume:
{resume_text}
{job_section}

Provide your analysis in the following JSON structure (IMPORTANT: Return ONLY valid JSON, no markdown, no explanations):

{{
    "atsScore": <number between 0-100>,
    "strengths": [<array of 3-5 key strengths as strings>],
    "improvements": [<array of 3-5 areas to improve as strings>],
    "missingKeywords": [<array of 3-5 important missing keywords as strings{keyword_note}>],
    "suggestions": [<array of 3-5 actionable suggestions as strings>]
}}

Focus on:
- ATS compatibility and formatting
- Keyword optimization
- Content quality and impact
- Achievement quantification
- Professional presentation
{alignment_note}

CRITICAL: Return ONLY the JSON object. No markdown code blocks, no explanations.
"""
        return prompt

    async def analyze_resume(
        self,
        resume_text: str,
        job_description: str = ""
    ) -> AnalysisResult:
        """
        Analyze resume using Groq API
        """

        log_service_call(
            "GroqService",
            "analyze_resume",
            f"Resume length: {len(resume_text)}, Job desc: {'Yes' if job_description else 'No'}"
        )

        try:
            # Build prompt
            prompt = self._build_analysis_prompt(resume_text, job_description)

            logger.info("Calling Groq API...")
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert resume analyzer and ATS optimization specialist. "
                            "Return ONLY valid JSON. No markdown. No explanations."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS
            )

            response_content = response.choices[0].message.content
            logger.info(f"Groq API response received ({len(response_content)} chars)")

            analysis_data = self._parse_response(response_content)

            result = AnalysisResult(**analysis_data)
            logger.info(f"Resume analysis successful. ATS Score: {result.atsScore}")

            return result

        except json.JSONDecodeError as e:
            log_error(e, "Groq JSON parsing")
            raise GroqAPIError(
                "Failed to parse Groq API response",
                details=str(e)
            )

        except Exception as e:
            log_error(e, "Groq analyze_resume")
            raise GroqAPIError(
                "Failed to analyze resume with Groq API",
                details=str(e)
            )

    def _parse_response(self, response_content: str) -> Dict[str, Any]:
        """
        Parse and clean Groq API response
        """

        content = response_content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```"):
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                content = content[start:end]

        data = json.loads(content)

        required_fields = [
            "atsScore",
            "strengths",
            "improvements",
            "missingKeywords",
            "suggestions"
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return data


# ✅ Global instance
groq_service = GroqService()
