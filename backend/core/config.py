"""
config.py — Pydantic settings for DocForge AI + CiteRAG
========================================================

All values read from environment / .env file.
Add .env to .gitignore — never commit secrets.

Required .env keys:
  AZURE_LLM_ENDPOINT
  AZURE_OPENAI_LLM_KEY
  AZURE_LLM_DEPLOYMENT_41_MINI
  AZURE_EMB_ENDPOINT
  AZURE_OPENAI_EMB_KEY
  AZURE_EMB_DEPLOYMENT
  AZURE_EMB_API_VERSION
  NOTION_TOKEN
  NOTION_DATABASE_ID          ← source document DB for RAG ingest
  NOTION_TICKET_DB_ID         ← ticket tracking DB for agent layer
  CHROMA_PATH
  REDIS_URL
  DATABASE_URL                ← PostgreSQL
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Azure OpenAI — LLM ────────────────────────────────────────────────────
    AZURE_LLM_ENDPOINT:            str = ""
    AZURE_OPENAI_LLM_KEY:          str = ""
    AZURE_LLM_DEPLOYMENT_41_MINI:  str = "gpt-4.1-mini"
    AZURE_LLM_API_VERSION:         str = "2024-12-01-preview"

    # ── Azure OpenAI — Embeddings ─────────────────────────────────────────────
    AZURE_EMB_ENDPOINT:            str = ""
    AZURE_OPENAI_EMB_KEY:          str = ""
    AZURE_EMB_DEPLOYMENT:          str = "text-embedding-3-large"
    AZURE_EMB_API_VERSION:         str = "2024-02-01"

    # ── Notion ────────────────────────────────────────────────────────────────
    NOTION_TOKEN:                  str = ""       # preferred key name
    NOTION_API_KEY:                str = ""       # legacy key name (alias fallback)
    NOTION_DATABASE_ID:            str = ""       # Source docs DB
    NOTION_TICKET_DB_ID:           Optional[str] = None  # Ticket tracking DB

    # ── Vector store ──────────────────────────────────────────────────────────
    CHROMA_PATH:                   str = ""

    # ── Cache ─────────────────────────────────────────────────────────────────
    REDIS_URL:                     str = "redis://localhost:6379/0"

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL:                  str = "postgresql://user:pass@localhost:5432/docforge"

    # ── App ───────────────────────────────────────────────────────────────────
    APP_ENV:                       str = "development"
    LOG_LEVEL:                     str = "INFO"

    def model_post_init(self, __context):
        """Pydantic v2 lifecycle hook — runs after model initialization."""
        # Resolve CHROMA_PATH to absolute path
        if not self.CHROMA_PATH:
            self.CHROMA_PATH = str(Path(__file__).parent.parent.parent / "chroma_db")
        else:
            self.CHROMA_PATH = str(Path(self.CHROMA_PATH).resolve())
        # Auto-create directory if it doesn't exist
        Path(self.CHROMA_PATH).mkdir(parents=True, exist_ok=True)


settings = Settings()