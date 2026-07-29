from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models import InterviewSession, Question
from app.schemas import SummaryOut, TranscriptItem
from app.llm import generate_session_insight

router = APIRouter()


@router.get("/sessions/{session_id}/summary", response_model=SummaryOut)
def get_summary(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    questions = sorted(session.questions, key=lambda q: q.order_index)
    answered = [q for q in questions if q.answer_text]
    avg_len = (
        sum(len(q.answer_text.split()) for q in answered) / len(answered)
        if answered else 0.0
    )
    topics = sorted({q.source_topic for q in questions if q.source_topic})

    transcript = [
        TranscriptItem(
            order_index=q.order_index,
            question_text=q.question_text,
            source_topic=q.source_topic,
            triggering_skill=q.triggering_skill,
            retrieved_context=q.retrieved_context,
            answer_text=q.answer_text,
        )
        for q in questions
    ]

    insight = generate_session_insight(session.role_label, session.extracted_skills, topics)

    return SummaryOut(
        session_id=session.id,
        role_label=session.role_label,
        extracted_skills=session.extracted_skills or [],
        total_questions=len(questions),
        answered_questions=len(answered),
        average_answer_length=round(avg_len, 1),
        topics_covered=topics,
        transcript=transcript,
        insight=insight,
    )
