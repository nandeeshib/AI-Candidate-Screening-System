import random
from app.rag.retrieve import retrieve
from app.llm import generate_question
from app.config import ROLES

GENERAL_TOPICS_BY_ROLE = {
    "ai_ml_engineer": ["model evaluation", "retrieval augmented generation", "overfitting"],
    "backend_engineer": ["API design", "database modeling", "system scalability"],
    "data_scientist": ["hypothesis testing", "exploratory data analysis", "model interpretability"],
}


def build_query_queue(role_id: str, skills: list[str], max_questions: int = 6) -> list[dict]:
    """Context Construction step: turns extracted resume skills + role into a queue
    of (skill, query) pairs that will each drive one retrieval + question generation."""
    role_label = ROLES.get(role_id, role_id)
    queue = []

    skills_sample = skills[:] 
    random.shuffle(skills_sample)
    for skill in skills_sample:
        queue.append({"skill": skill, "query": f"{skill} in the context of {role_label}"})

    for topic in GENERAL_TOPICS_BY_ROLE.get(role_id, []):
        queue.append({"skill": None, "query": f"{topic} for a {role_label}"})

    if not queue:
        queue.append({"skill": None, "query": f"core concepts for a {role_label}"})

    return queue[:max_questions]


def generate_next_question(role_id: str, queue_item: dict) -> dict:
    """Knowledge Retrieval + Question Generation steps for a single queue item."""
    role_label = ROLES.get(role_id, role_id)
    skill = queue_item.get("skill")
    query = queue_item["query"]

    retrieved = retrieve(role_id, query, top_k=3)
    if not retrieved:
        top_chunk = {"topic": "General", "text": "No specific reference material found."}
    else:
        top_chunk = retrieved[0]

    combined_context = "\n\n".join(r["text"] for r in retrieved[:2]) if retrieved else top_chunk["text"]

    question_text, method = generate_question(
        role_label=role_label,
        skill=skill,
        topic=top_chunk["topic"],
        context=combined_context,
    )

    return {
        "question_text": question_text,
        "source_topic": top_chunk["topic"],
        "retrieved_context": combined_context,
        "triggering_skill": skill,
        "generation_method": method,
    }


def pick_adaptive_next(queue: list[dict], last_answer_text: str) -> dict | None:
    """Optional adaptivity: if the previous answer was short/thin, prefer a queued
    item tied to a concrete skill (more grounded/easier) over a general topic;
    if the previous answer was long/detailed, prefer a general/deeper topic next."""
    if not queue:
        return None
    answer_len = len((last_answer_text or "").split())
    skill_items = [q for q in queue if q.get("skill")]
    general_items = [q for q in queue if not q.get("skill")]

    if answer_len < 25 and skill_items:
        chosen = skill_items[0]
    elif general_items:
        chosen = general_items[0]
    else:
        chosen = queue[0]

    queue.remove(chosen)
    return chosen
