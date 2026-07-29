from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import upload, interview, results
from app.rag.ingest import build_all_indexes

app = FastAPI(
    title="AI Candidate Screening System",
    description="RAG-powered role-based technical interview screener",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for a local take-home demo; restrict in real production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["setup"])
app.include_router(interview.router, tags=["interview"])
app.include_router(results.router, tags=["results"])


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    build_all_indexes()


@app.get("/health")
def health():
    from app.llm import llm_available
    return {"status": "ok", "llm_mode": "groq" if llm_available() else "template_fallback"}
