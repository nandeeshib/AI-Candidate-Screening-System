from pydantic import BaseModel
from typing import List, Optional


class RoleOut(BaseModel):
    id: str
    label: str


class SessionCreateOut(BaseModel):
    session_id: str
    role_id: str
    role_label: str
    extracted_skills: List[str]
    resume_filename: Optional[str] = None


class QuestionOut(BaseModel):
    question_id: str
    order_index: int
    question_text: str
    source_topic: Optional[str] = None
    triggering_skill: Optional[str] = None
    generation_method: Optional[str] = None
    total_questions: int


class AnswerIn(BaseModel):
    session_id: str
    question_id: str
    answer_text: str


class AnswerOut(BaseModel):
    ok: bool
    next_question: Optional[QuestionOut] = None
    completed: bool = False


class TranscriptItem(BaseModel):
    order_index: int
    question_text: str
    source_topic: Optional[str]
    triggering_skill: Optional[str]
    retrieved_context: Optional[str]
    answer_text: Optional[str]


class SummaryOut(BaseModel):
    session_id: str
    role_label: str
    extracted_skills: List[str]
    total_questions: int
    answered_questions: int
    average_answer_length: float
    topics_covered: List[str]
    transcript: List[TranscriptItem]
    insight: str
