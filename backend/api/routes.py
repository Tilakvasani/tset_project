from fastapi import APIRouter, HTTPException
from backend.schemas.document_schema import DocumentRequest, DocumentResponse
from backend.schemas.notion_schema import NotionPublishRequest
from backend.services.generator import generate_document
from backend.services.notion_service import publish_to_notion, get_documents_from_notion
from backend.services.redis_service import get_cached_doc, cache_doc
from backend.services.db_service import update_notion_url, get_all_documents
from backend.core.logger import logger

router = APIRouter()

@router.post("/generate", response_model=DocumentResponse)
async def generate(request: DocumentRequest):
    """Generate a document — saves to PostgreSQL with all 7 section answers"""
    try:
        logger.info(f"Generating {request.doc_type} for {request.industry} | dept: {request.department}")

        cache_key = f"{request.industry}:{request.doc_type}:{request.title}"
        cached = get_cached_doc(cache_key)
        if cached:
            logger.info("Returning cached document")
            return cached

        result = await generate_document(request)
        cache_doc(cache_key, result)
        return result

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish")
async def publish(request: NotionPublishRequest):
    """Publish to Notion — then update PostgreSQL with notion_url"""
    try:
        logger.info(f"Publishing doc {request.doc_id} to Notion")
        notion_url = await publish_to_notion(request)

        # Extract page ID from URL and update PostgreSQL
        try:
            page_id = notion_url.rstrip("/").split("-")[-1] if notion_url else ""
            await update_notion_url(request.doc_id, notion_url, page_id)
        except Exception as db_err:
            logger.warning(f"Failed to update notion_url in PostgreSQL: {db_err}")

        return {"success": True, "notion_url": notion_url}
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/library")
async def library(department: str = None, doc_type: str = None, status: str = None):
    """Get all documents — from PostgreSQL with optional filters"""
    try:
        # Try PostgreSQL first, fall back to Notion
        try:
            docs = await get_all_documents(
                department=department,
                doc_type=doc_type,
                status=status,
            )
            if docs:
                return {"total": len(docs), "documents": docs, "source": "postgresql"}
        except Exception as db_err:
            logger.warning(f"PostgreSQL library fetch failed, falling back to Notion: {db_err}")

        docs = await get_documents_from_notion()
        return {"total": len(docs), "documents": docs, "source": "notion"}
    except Exception as e:
        logger.error(f"Library fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))