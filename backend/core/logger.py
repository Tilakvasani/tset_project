"""
logger.py — Pretty PowerShell-friendly logging for CiteRAG / DocForge

Output format:
  14:32:05  ℹ  Redis connected
  14:32:05  ✅ Agent compiled — nodes: [...]
  14:32:08  ⚠️  Classifier LLM failed — defaulting to DOCUMENT
  14:32:09  ❌ create_ticket error: ...
"""

import logging
import sys
from backend.core.config import settings


# ── Emoji map per level ───────────────────────────────────────────────────────
_LEVEL_EMOJI = {
    logging.DEBUG:    "🔎",
    logging.INFO:     "ℹ️ ",
    logging.WARNING:  "⚠️ ",
    logging.ERROR:    "❌",
    logging.CRITICAL: "🔥",
}

# Shorten noisy module names for cleaner output
_MODULE_ALIASES = {
    "backend.agents.agent_graph":         "agent",
    "backend.api.agent_routes":           "routes",
    "backend.rag.rag_service":            "rag",
    "backend.api.rag_routes":             "rag_api",
    "backend.rag.ticket_dedup":           "dedup",
    "backend.rag.ragas_scorer":           "ragas",
    "backend.rag.ingest_service":         "ingest",
    "backend.services.redis_service":     "redis",
    "backend.core.logger":                "core",
    "ai-doc-generator":                   "app",
    "uvicorn":                            "uvicorn",
    "uvicorn.error":                      "uvicorn",
    "uvicorn.access":                     "access",
    "fastapi":                            "fastapi",
}


class _PrettyFormatter(logging.Formatter):
    """
    Compact, emoji-prefixed formatter for console output.
    
    Generates a log line in the format:
      [HH:MM:SS] [EMOJI] [MODULE] [MESSAGE]
    
    Attributes:
        datefmt (str): Format string for the timestamp.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a LogRecord into a pretty console string.
        
        Args:
            record: The logging.LogRecord to format.
            
        Returns:
            The formatted string with emoji and shortened module names.
        """
        # Time — only HH:MM:SS, no date
        time_str = self.formatTime(record, "%H:%M:%S")

        # Emoji for level
        emoji = _LEVEL_EMOJI.get(record.levelno, "  ")

        # Short module name
        module = _MODULE_ALIASES.get(record.name, record.name.split(".")[-1])

        # Message
        msg = record.getMessage()

        # Attach exception if present
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            # indent exception lines for readability
            exc_lines = "\n".join("      " + l for l in exc_text.splitlines())
            msg = f"{msg}\n{exc_lines}"

        return f"  {time_str}  {emoji}  [{module}]  {msg}"


def _setup_logging():
    """
    Initializes the global logging configuration.

    - Sets the log level from settings.
    - Attaches the _PrettyFormatter to the stream handler.
    - Silences noisy third-party libraries (httpx, urllib3, etc.).
    - Configures uvicorn access logs to be less verbose in production.

    CRASH FIX (Windows / Python 3.11 SpawnProcess):
      We must NOT call logging.basicConfig(force=True) inside a uvicorn
      spawned sub-process.  force=True replaces ALL existing handlers on the
      root logger — including the ones uvicorn sets up via dictConfig — which
      triggers the 'configure_custom' traceback on every hot-reload.
      Instead we attach our handler only when the root logger has no
      StreamHandler pointing at stdout yet (first-time setup), and in all
      other cases we simply set the level and let uvicorn's own handlers
      remain in place.
    """
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # Only add our pretty handler if no stdout StreamHandler exists yet.
    # This prevents double-printing on reload and avoids the dictConfig crash.
    already_has_stdout = any(
        isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stdout
        for h in root.handlers
    )
    if not already_has_stdout:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_PrettyFormatter())
        handler.setLevel(level)
        root.addHandler(handler)
    else:
        # Re-apply our formatter to the existing stdout handler so log style
        # is consistent even after uvicorn re-installs its own handlers.
        for h in root.handlers:
            if isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stdout:
                h.setFormatter(_PrettyFormatter())
                h.setLevel(level)

    for noisy in ("httpx", "httpcore", "urllib3", "asyncio", "langsmith"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    if level > logging.DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


# _setup_logging() is now called by main.py lifespan

logger = logging.getLogger("app")