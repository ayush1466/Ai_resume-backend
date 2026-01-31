import re

RESUME_KEYWORDS = [
    "resume", "curriculum vitae", "education", "experience",
    "skills", "projects", "internship", "certification",
    "objective", "summary"
]

def looks_like_resume(text: str) -> bool:
    if not text or len(text) < 500:
        return False

    text_lower = text.lower()
    score = 0

    for kw in RESUME_KEYWORDS:
        if kw in text_lower:
            score += 1

    # Email check
    if re.search(r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b", text):
        score += 1

    # Phone number check (Indian + general)
    if re.search(r"\b\d{10}\b", text):
        score += 1

    return score >= 3
