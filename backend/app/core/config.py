"""
Application Configuration — Pydantic Settings v2
All secrets are loaded from backend/.env — never hard-coded.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────
    APP_NAME: str = "Smart Farming Advisor"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-change-me"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # ── Database ─────────────────────────────────────────────────────────
    # asyncpg URL — no psycopg2 needed (py3.14 compatible)
    DATABASE_URL: str = "postgresql+asyncpg://farmer_user:farmer_pass@localhost:5432/farming_db"

    # ── IBM WatsonX / Granite ─────────────────────────────────────────────
    WATSONX_API_KEY: str = ""
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    GRANITE_MODEL_ID: str = "ibm/granite-13b-instruct-v2"

    # ── ChromaDB ──────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "farming_knowledge"

    # ── Embeddings ────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"


    # ── Market ────────────────────────────────────────────────────────────
    AGMARKNET_API_URL: str = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    AGMARKNET_API_KEY: str = ""

    # ── JWT ───────────────────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080   # 7 days

    # ── RAG ───────────────────────────────────────────────────────────────
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5
    MIN_RELEVANCE_SCORE: float = 0.3

    # ── Speech ────────────────────────────────────────────────────────────
    SPEECH_LANGUAGE: str = "en-IN"
    TTS_LANGUAGE: str = "en"

    # ── Computed helpers ──────────────────────────────────────────────────
    @property
    def origins_list(self) -> List[str]:
        """Return ALLOWED_ORIGINS as a Python list."""
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def ibm_configured(self) -> bool:
        """True when both IBM credentials look real (not placeholders)."""
        return (
            bool(self.WATSONX_API_KEY)
            and "PASTE_YOUR" not in self.WATSONX_API_KEY
            and bool(self.WATSONX_PROJECT_ID)
            and "PASTE_YOUR" not in self.WATSONX_PROJECT_ID
        )


# Single shared instance — import this everywhere
settings = Settings()
