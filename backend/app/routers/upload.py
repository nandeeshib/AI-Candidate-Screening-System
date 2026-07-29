from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models import InterviewSession, Question
from app.schemas import RoleOut, SessionCreateOut, QuestionOut
from app.config import ROLES
from app.resume_parser import extract_text, extract_skills
from app.interview_engine import build_query_queue, generate_next_question

router = APIRouter()


@router.get("/roles", response_model=list[RoleOut])
def list_roles():
    return [{"id": rid, "label": label} for rid, label in ROLES.items()]


@router.post("/sessions", response_model=SessionCreateOut)
async def create_session(
    role_id: str = Form(...),
    resume: UploadFile = File(...),
    db: DBSession = Depends(get_db),
):
    if role_id not in ROLES:
        raise HTTPException(status_code=400, detail=f"Unknown role_id '{role_id}'")

    file_bytes = await resume.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded resume file is empty")

    try:
        resume_text = extract_text(resume.filename, file_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse resume: {e}")

    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from this resume (is it a scanned image PDF?).",
        )

    skills = extract_skills(resume_text)

    session = InterviewSession(
        role_id=role_id,
        role_label=ROLES[role_id],
        resume_filename=resume.filename,
        resume_text=resume_text[:20000],  # cap stored size
        extracted_skills=skills,
        status="created",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionCreateOut(
        session_id=session.id,
        role_id=session.role_id,
        role_label=session.role_label,
        extracted_skills=skills,
        resume_filename=session.resume_filename,
    )
