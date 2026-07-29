import io
import re
import pdfplumber
from app.config import SKILL_KEYWORDS


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text(filename: str, file_bytes: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    # plain text fallback
    return file_bytes.decode("utf-8", errors="ignore")


def extract_skills(resume_text: str) -> list[str]:
    """Lightweight, dependency-free skill extraction via keyword matching.
    Matches whole words/phrases so 'go' doesn't match inside 'going', etc."""
    text_lower = resume_text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


def estimate_experience_years(resume_text: str) -> int | None:
    """Best-effort heuristic: looks for patterns like '3 years of experience'."""
    match = re.search(r"(\d{1,2})\+?\s*years?\s+(of\s+)?experience", resume_text.lower())
    if match:
        return int(match.group(1))
    return None
