# Panel — AI-Powered Role-Based Candidate Screening System

A RAG-driven technical screening interviewer. A candidate uploads a resume and picks a role;
the system extracts skills, retrieves grounded context from a role-specific knowledge base,
generates targeted interview questions, runs an interactive Q&A session, and produces a
structured summary.

Built for the PG-AGI AI/ML & Backend Engineering Intern assignment.

---

## 1. Architecture

```
frontend (React + Vite)  <--HTTP-->  backend (FastAPI)
                                        |
                                        |-- resume_parser.py     (PDF -> text -> skill keywords)
                                        |-- interview_engine.py  (orchestration: query building, adaptivity)
                                        |-- rag/ingest.py        (chunk KB docs -> embeddings -> FAISS index)
                                        |-- rag/retrieve.py      (query -> top-k relevant chunks)
                                        |-- llm.py               (Groq LLM call, with template fallback)
                                        |-- models.py            (SQLAlchemy: sessions, questions/answers)
                                        |
                                        v
                                  SQLite (screener.db)   +   FAISS index (vector_index/)
```

**Pipeline per question:** resume skill + role → query → FAISS retrieval (top-k chunks from the
role's knowledge base) → LLM (or template) generates a question grounded in that retrieved text →
question + its source chunk + triggering skill are stored together, so every question is
traceable back to *why* it was asked.

## 2. Key design decisions

- **FAISS + sentence-transformers (`all-MiniLM-L6-v2`)** for retrieval — runs fully locally, no
  paid vector DB needed, good enough recall for a knowledge base this size.
- **Topic-based chunking**: the knowledge base files are written as labeled `TOPIC:` blocks, so
  each chunk is a coherent, self-contained concept rather than an arbitrary token window. This
  avoids splitting an idea across chunk boundaries.
- **Groq for generation, with a template fallback**: Groq's free tier needs no credit card and is
  fast. If `GROQ_API_KEY` isn't set (or a call fails), the system automatically falls back to
  filling structured templates with the same retrieved context, so the app is never blocked on
  having a key — it just produces less varied questions.
- **Adaptive sequencing**: after each answer, the next question is chosen based on the previous
  answer's length — a short answer routes to another skill-grounded (typically easier/more
  concrete) question next; a long, detailed answer routes to a general/deeper topic. This is the
  "questions may adapt" optional requirement from the brief.
- **SQLite** for persistence — zero setup, stores sessions, every question, its retrieved
  context, and the candidate's answer, so the full pipeline is auditable end to end.

## 3. Knowledge base

`backend/app/knowledge_base/*.txt` contains original, hand-written reference notes (not copied
from any textbook, for licensing cleanliness) covering core concepts for three roles:
`ai_ml_engineer`, `backend_engineer`, `data_scientist`. Add more roles by dropping a new
`<role_id>.txt` file there (using the same `TOPIC: ...` block format) and adding it to `ROLES` in
`backend/app/config.py`.

## 4. Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com/keys) (optional — the app works without one)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# open .env and paste your GROQ_API_KEY (optional)

uvicorn app.main:app --reload --port 8000
```
First startup downloads the small embedding model (~90 MB) and builds the FAISS indexes — this
needs internet access once, then everything runs offline.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173**. The dev server proxies `/api/*` to the backend on port 8000.

### Without a Groq key
Leave `GROQ_API_KEY` blank in `.env`. The app still runs fully — questions are assembled from
templates filled with real retrieved context instead of freely generated. Get a free key any time
at console.groq.com and restart the backend to switch to full LLM generation.

## 5. Using it
1. Pick a role, upload a resume (PDF or `.txt`) → skills are extracted automatically.
2. Review the detected skills, start the interview.
3. Answer each question (grounded context + triggering skill shown as tags).
4. After the last question, view the summary: stats, an AI-generated closing insight, and the
   full transcript with each question's source topic.

## 6. Possible extensions
- Score answers against retrieved reference text using embedding similarity (semantic grading)
- Multi-turn follow-up questions on a single topic before moving on
- Interviewer-side dashboard to compare multiple candidates for the same role
- Swap SQLite for Postgres + a managed vector DB (Pinecone/Qdrant) for multi-user production use
