import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models import InterviewSession, Question
from app.schemas import QuestionOut, AnswerIn, AnswerOut
from app.interview_engine import build_query_queue, generate_next_question, pick_adaptive_next

router = APIRouter()

MAX_QUESTIONS = 6


def _to_question_out(q: Question, total: int) -> QuestionOut:
    return QuestionOut(
        question_id=q.id,
        order_index=q.order_index,
        question_text=q.question_text,
        source_topic=q.source_topic,
        triggering_skill=q.triggering_skill,
        generation_method=q.generation_method,
        total_questions=total,
    )


@router.post("/interview/{session_id}/start", response_model=QuestionOut)
def start_interview(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.questions:
        first = sorted(session.questions, key=lambda q: q.order_index)[0]
        return _to_question_out(first, MAX_QUESTIONS)

    queue = build_query_queue(session.role_id, session.extracted_skills, max_questions=MAX_QUESTIONS)
    first_item = queue.pop(0)
    generated = generate_next_question(session.role_id, first_item)

    question = Question(
        session_id=session.id,
        order_index=0,
        **generated,
    )
    db.add(question)
    session.pending_queue = queue
    session.status = "in_progress"
    db.commit()
    db.refresh(question)

    return _to_question_out(question, MAX_QUESTIONS)


@router.post("/interview/answer", response_model=AnswerOut)
def submit_answer(payload: AnswerIn, db: DBSession = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question or question.session_id != session.id:
        raise HTTPException(status_code=404, detail="Question not found for this session")

    question.answer_text = payload.answer_text
    question.answer_submitted_at = datetime.datetime.utcnow()
    db.commit()

    queue = list(session.pending_queue or [])
    next_item = pick_adaptive_next(queue, payload.answer_text)

    if next_item is None:
        session.status = "completed"
        session.pending_queue = []
        db.commit()
        return AnswerOut(ok=True, next_question=None, completed=True)

    generated = generate_next_question(session.role_id, next_item)
    next_question = Question(
        session_id=session.id,
        order_index=question.order_index + 1,
        **generated,
    )
    db.add(next_question)
    session.pending_queue = queue
    db.commit()
    db.refresh(next_question)

    return AnswerOut(
        ok=True,
        next_question=_to_question_out(next_question, MAX_QUESTIONS),
        completed=False,
    )
