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
    """
    Application settings and environment configuration.
    
    Loads values from a .env file or environment variables. This class
    centrally manages credentials for Azure OpenAI, Notion, Redis, 
    and general application behavior.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Azure OpenAI — LLM ────────────────────────────────────────────────────
    AZURE_LLM_ENDPOINT:            str = ""                  # Azure endpoint URL
    AZURE_OPENAI_LLM_KEY:          str = ""                  # Azure API key
    AZURE_LLM_DEPLOYMENT_41_MINI:  str = "gpt-4.1-mini"      # Deployment name
    AZURE_LLM_API_VERSION:         str = "2024-12-01-preview" # API version

    # ── Azure OpenAI — Embeddings ─────────────────────────────────────────────
    AZURE_EMB_ENDPOINT:            str = ""                  # Embeddings endpoint URL
    AZURE_OPENAI_EMB_KEY:          str = ""                  # Embeddings API key
    AZURE_EMB_DEPLOYMENT:          str = "text-embedding-3-large" 
    AZURE_EMB_API_VERSION:         str = "2024-02-01"

    # ── Notion ────────────────────────────────────────────────────────────────
    NOTION_TOKEN:                  str = ""       # Main integration token
    NOTION_API_KEY:                str = ""       # Legacy fallback alias
    NOTION_DATABASE_ID:            str = ""       # ID of the RAG source database
    NOTION_TICKET_DB_ID:           Optional[str] = None  # ID of the ticket tracking database

    # ── Vector store ──────────────────────────────────────────────────────────
    CHROMA_PATH:                   str = ""       # Absolute path to ChromaDB storage

    # ── Cache ─────────────────────────────────────────────────────────────────
    REDIS_URL:                     str = "redis://localhost:6379/0"

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL:                  str = "postgresql://user:pass@localhost:5432/docforge"

    # ── App ───────────────────────────────────────────────────────────────────
    APP_ENV:                       str = "development"
    LOG_LEVEL:                     str = "INFO"

    def model_post_init(self, __context):
        """
        Pydantic v2 lifecycle hook.
        
        Finalizes configuration after the model is initialized:
        - Resolves CHROMA_PATH to an absolute path.
        - Ensures the storage directory exists.
        """
        # Resolve CHROMA_PATH to absolute path
        if not self.CHROMA_PATH:
            self.CHROMA_PATH = str(Path(__file__).parent.parent.parent / "chroma_db")
        else:
            self.CHROMA_PATH = str(Path(self.CHROMA_PATH).resolve())
        # Auto-create directory if it doesn't exist
        Path(self.CHROMA_PATH).mkdir(parents=True, exist_ok=True)


settings = Settings()