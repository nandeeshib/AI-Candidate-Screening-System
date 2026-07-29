import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./screener.db")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "4"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
INDEX_DIR = os.path.join(BASE_DIR, "vector_index")

ROLES = {
    "ai_ml_engineer": "AI/ML Engineer",
    "backend_engineer": "Backend Engineer",
    "data_scientist": "Data Scientist / Applied ML",
}

# Keyword list used for lightweight resume skill extraction (no external NLP service required)
SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "nosql", "postgresql", "mysql", "mongodb", "redis", "sqlite",
    "fastapi", "flask", "django", "node.js", "express", "spring boot",
    "react", "next.js", "vue", "angular",
    "machine learning", "deep learning", "neural network", "nlp",
    "computer vision", "pytorch", "tensorflow", "keras", "scikit-learn",
    "pandas", "numpy", "data analysis", "data visualization",
    "rag", "retrieval augmented generation", "llm", "langchain",
    "vector database", "faiss", "chromadb", "embeddings",
    "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "git",
    "microservices", "rest api", "graphql", "system design",
    "statistics", "a/b testing", "etl", "airflow", "spark", "hadoop",
]
