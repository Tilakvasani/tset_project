"""
llm.py — Shared Azure LLM factory for DocForge AI + CiteRAG
=============================================================

Single source of truth for all AzureChatOpenAI instances.
Fixes:
  - H2: Race-condition-free eager singleton for the default LLM.
  - M1: Reads api_version from settings instead of hardcoding it.

Usage:
    from backend.core.llm import get_llm

    llm = get_llm()            # default singleton (temp=0.2, max_tokens=3000)
    llm = get_llm(temperature=0.0)  # fresh instance for one-off tasks
"""

# ── Internal ──────────────────────────────────────────────────────────────────
from backend.core.config import settings

# ── Third-party ───────────────────────────────────────────────────────────────
from langchain_openai import AzureChatOpenAI

# ─────────────────────────────────────────────────────────────────────────────
#  Eager singleton — initialized once at import time, no race condition possible
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULT_LLM: AzureChatOpenAI = AzureChatOpenAI(
    azure_endpoint=settings.AZURE_LLM_ENDPOINT,
    api_key=settings.AZURE_OPENAI_LLM_KEY,
    azure_deployment=settings.AZURE_LLM_DEPLOYMENT_41_MINI,
    api_version=settings.AZURE_LLM_API_VERSION,   # M1 FIX: from settings, not hardcoded
    temperature=0.2,
    max_tokens=3000,
)


def get_llm(temperature: float = 0.2, max_tokens: int = 3000) -> AzureChatOpenAI:
    """
    Returns an AzureChatOpenAI instance.

    - For default params (temp=0.2, max_tokens=3000): returns the module-level
      singleton — safe under all concurrency, zero construction overhead.
    - For custom params: returns a fresh instance for specialized tasks
      (e.g. summarization at temp=0.0).
    """
    if temperature == 0.2 and max_tokens == 3000:
        return _DEFAULT_LLM

    return AzureChatOpenAI(
        azure_endpoint=settings.AZURE_LLM_ENDPOINT,
        api_key=settings.AZURE_OPENAI_LLM_KEY,
        azure_deployment=settings.AZURE_LLM_DEPLOYMENT_41_MINI,
        api_version=settings.AZURE_LLM_API_VERSION,
        temperature=temperature,
        max_tokens=max_tokens,
    )
