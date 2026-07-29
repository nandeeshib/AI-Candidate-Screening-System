import random
from app.config import GROQ_API_KEY, GROQ_MODEL

_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None and GROQ_API_KEY:
        from groq import Groq
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


def llm_available() -> bool:
    return bool(GROQ_API_KEY)


QUESTION_PROMPT = """You are a senior technical interviewer conducting a screening interview \
for the role of {role_label}.

Candidate background (skill mentioned on their resume): {skill}

Use ONLY the following reference material as grounding for the question. Do not invent facts \
outside of it:
---
{context}
---

Write exactly ONE interview question that:
- Tests conceptual and/or applied understanding of the topic above
- Is naturally connected to the candidate's stated skill ("{skill}") where possible
- Is specific, not generic (avoid "What is X?" style questions where possible)
- Is answerable in 2-5 sentences by a well-prepared candidate

Return ONLY the question text, with no preamble, numbering, or quotation marks."""


def generate_question_llm(role_label: str, skill: str, topic: str, context: str) -> str:
    client = _get_groq_client()
    prompt = QUESTION_PROMPT.format(role_label=role_label, skill=skill or topic, context=context)
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150,
    )
    question = completion.choices[0].message.content.strip()
    return question.strip('"').strip()


# --- Template fallback (used automatically when no GROQ_API_KEY is configured) ---
# These templates are combined with real retrieved context, so questions are still
# grounded in the knowledge base and influenced by the resume skill, they're just
# assembled rather than freely generated.
_TEMPLATES = [
    "Based on your experience with {skill}, how would you explain {topic} to a teammate who has never encountered it, and where might it go wrong in practice?",
    "Given your background in {skill}, walk me through a scenario where understanding {topic} would directly change a decision you made.",
    "How does {topic} relate to the way you've used {skill}? Give a concrete example from a project you've worked on.",
    "If a system you built using {skill} started behaving unexpectedly, how might concepts from {topic} help you diagnose the issue?",
    "What's a common misconception about {topic} that someone with hands-on {skill} experience would be able to correct?",
]


def generate_question_template(role_label: str, skill: str, topic: str, context: str) -> str:
    template = random.choice(_TEMPLATES)
    return template.format(skill=skill or "this area", topic=topic.lower())


def generate_question(role_label: str, skill: str, topic: str, context: str) -> tuple[str, str]:
    """Returns (question_text, method) where method is 'llm' or 'template'."""
    if llm_available():
        try:
            return generate_question_llm(role_label, skill, topic, context), "llm"
        except Exception:
            # Fail safe: if the API call errors (bad key, rate limit, network), don't crash the interview
            return generate_question_template(role_label, skill, topic, context), "template"
    return generate_question_template(role_label, skill, topic, context), "template"


SUMMARY_INSIGHT_TEMPLATES = [
    "Covered {n} topic areas grounded in the {role_label} knowledge base, with questions shaped by {skills}.",
]


def generate_session_insight(role_label: str, skills: list[str], topics: list[str]) -> str:
    """One-line AI-generated (or template) closing insight for the summary screen."""
    skills_str = ", ".join(skills[:5]) if skills else "general role knowledge"
    if llm_available():
        client = _get_groq_client()
        try:
            prompt = (
                f"In 2-3 sentences, give a neutral, constructive closing observation for a "
                f"screening interview summary for a {role_label} candidate. Skills detected on "
                f"resume: {skills_str}. Topics covered: {', '.join(topics)}. "
                f"Do not invent a score. Be specific, not generic."
            )
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=150,
            )
            return completion.choices[0].message.content.strip()
        except Exception:
            pass
    return (
        f"This session covered {len(topics)} topic area(s) relevant to {role_label}, "
        f"with questions influenced by the candidate's stated experience in {skills_str}. "
        f"Review the transcript below for depth and clarity of each answer."
    )
