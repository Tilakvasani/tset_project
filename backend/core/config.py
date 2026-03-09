from pathlib import Path
from pydantic_settings import BaseSettings

# Always resolve .env from project root regardless of where uvicorn is run from
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    # Groq
    GROQ_API_KEY: str = ""

    # Notion
    NOTION_API_KEY: str = ""
    NOTION_DATABASE_ID: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # App
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = str(ENV_FILE)

settings = Settings()

# Debug: print where .env is being loaded from
print(f"Loading .env from: {ENV_FILE}")
print(f"NOTION_API_KEY loaded: {'YES' if settings.NOTION_API_KEY else 'NO'}")
print(f"GROQ_API_KEY loaded: {'YES' if settings.GROQ_API_KEY else 'NO'}")