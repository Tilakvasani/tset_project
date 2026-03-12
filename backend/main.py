"""
DocForge AI — main.py
FastAPI application entry point.
Initializes DB connection pool and mounts all API routes.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.core.logger import logger
from backend.api.routes import router
from backend.services.db_service import get_pool, close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB pool. Shutdown: close DB pool."""
    logger.info("DocForge AI starting up...")
    try:
        pool = await get_pool()
        logger.info("✅ PostgreSQL connection pool ready")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

    yield

    logger.info("DocForge AI shutting down...")
    await close_pool()
    logger.info("✅ Database pool closed")


app = FastAPI(
    title="DocForge AI",
    description="AI-Powered Enterprise Document Generator",
    version="2.0.0",
    lifespan=lifespan
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "app": "DocForge AI",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check — verifies DB connection."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}