import uuid
import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def gen_id():
    return str(uuid.uuid4())


class InterviewSession(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=gen_id)
    role_id = Column(String, nullable=False)
    role_label = Column(String, nullable=False)
    resume_filename = Column(String, nullable=True)
    resume_text = Column(Text, nullable=True)
    extracted_skills = Column(JSON, default=list)
    pending_queue = Column(JSON, default=list)  # remaining (skill, query) pairs not yet asked
    status = Column(String, default="created")  # created -> in_progress -> completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=gen_id)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    order_index = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    source_topic = Column(String, nullable=True)          # which KB topic triggered this question
    retrieved_context = Column(Text, nullable=True)        # the chunk(s) used to ground the question
    triggering_skill = Column(String, nullable=True)       # which resume skill influenced this question
    generation_method = Column(String, nullable=True)      # "llm" or "template"
    answer_text = Column(Text, nullable=True)
    answer_submitted_at = Column(DateTime, nullable=True)

    session = relationship("InterviewSession", back_populates="questions")
