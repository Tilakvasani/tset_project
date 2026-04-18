"""
REST API Routes for core Document Generation functionality.
Handles fetching sections, generating content via LLM, and publishing to Notion.
"""
# ── Third-party ───────────────────────────────────────────────────────────────
from fastapi import APIRouter, HTTPException   # FastAPI routing + error responses
from pydantic import BaseModel                 # Request/response schema validation
from typing import List

# ── Internal ──────────────────────────────────────────────────────────────────
from backend.core.logger import logger         # Structured logger
from backend.services.db_service import (
    get_all_departments, get_sections_by_doc_type,
    save_generated_document,
)
from backend.services.generator import (
    generate_questions, save_user_answers,
    generate_section_content, edit_section,
)
from backend.services.notion_service import publish_to_notion, fetch_library_from_notion
from backend.schemas.document_schema import (
    GenerateQuestionsRequest, SaveAnswersRequest,
    GenerateSectionRequest, EditSectionRequest,
    NotionPublishRequest,
)
from backend.services.redis_service import cache   # Redis caching layer
from backend.prompts.quality_gates import check_quality    # PS1 quality gate validator

router = APIRouter()


class SaveDocRequest(BaseModel):
    doc_id: int
    doc_sec_id: int
    sec_id: int
    gen_doc_sec_dec: List[str]
    gen_doc_full: str



# ── Departments & Sections ────────────────────────────────────────────────────

@router.get("/departments")
async def get_departments():
    """
    Fetch the list of all available departments for document generation.
    Returns cached list if available to minimize database hits.
    """
    logger.info("📥 [GET /departments] Frontend requested department list")
    try:
        # Try cache first
        cached = await cache.get_departments()
        if cached is not None:
            logger.info("✅ [CACHE HIT] departments — returning %d depts from Redis", len(cached))
            return {"departments": cached, "total": len(cached), "cached": True}

        depts = await get_all_departments()
        logger.info("🗄️  [DB] Loaded %d departments from database", len(depts))

        # Store in cache
        await cache.set_departments(depts)
        logger.info("💾 [CACHE SET] departments (%d items)", len(depts))

        return {"departments": depts, "total": len(depts), "cached": False}
    except Exception as e:
        logger.error("❌ [GET /departments] Error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sections/{doc_type}")
async def get_sections(doc_type: str):
    """
    Retrieve the standard sections required for a specific document type.
    Decodes URL-encoded doc types and checks Redis cache first.
    """
    decoded = doc_type.replace("%2F", "/").replace("%28", "(").replace("%29", ")")
    logger.info("📥 [GET /sections] Frontend requested sections for doc_type=%r", decoded)
    try:
        # Try cache first
        cached = await cache.get_sections(decoded)
        if cached is not None:
            logger.info("✅ [CACHE HIT] sections:%s", decoded)
            return {**cached, "cached": True}

        sections = await get_sections_by_doc_type(decoded)
        if not sections:
            logger.warning("⚠️  [GET /sections] No sections found for doc_type=%r", decoded)
            raise HTTPException(status_code=404, detail=f"No sections for: {decoded}")

        sec_names = sections.get("doc_sec", [])
        logger.info("🗄️  [DB] Loaded %d sections for %r: %s", len(sec_names), decoded, sec_names)

        # Store in cache
        await cache.set_sections(decoded, sections)
        logger.info("💾 [CACHE SET] sections:%s", decoded)

        return {**sections, "cached": False}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ [GET /sections] Error for doc_type=%r: %s", decoded, e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Questions & Answers ───────────────────────────────────────────────────────

@router.post("/questions/generate")
async def api_generate_questions(req: GenerateQuestionsRequest):
    """
    Generate contextual questions for a specific document section using the LLM.
    These questions are presented to the user to gather dynamic facts.
    """
    logger.info(
        "📥 [POST /questions/generate] section=%r | doc_type=%r | dept=%r | company=%r",
        req.section_name, req.doc_type, req.department,
        (req.company_context or {}).get("company_name", "?"),
    )
    try:
        result = await generate_questions(req)

        questions = result.get("questions", [])
        sec_id = result.get("sec_id")
        logger.info(
            "✅ [POST /questions/generate] sec_id=%s | section=%r | %d questions generated: %s",
            sec_id, req.section_name, len(questions), questions,
        )

        if sec_id:
            await cache.set_questions(sec_id, result)
            logger.info("💾 [CACHE SET] questions:%s", sec_id)

        return result
    except Exception as e:
        logger.error("❌ [POST /questions/generate] section=%r error: %s", req.section_name, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answers/save")
async def api_save_answers(req: SaveAnswersRequest):
    """
    Save the user's answers against a specific section.
    Invalidates the cached section content to force a fresh regeneration.
    """
    logger.info(
        "📥 [POST /answers/save] sec_id=%s | section=%r | %d answers received",
        req.sec_id, req.section_name, len(req.answers or []),
    )
    for i, (q, a) in enumerate(zip(req.questions or [], req.answers or [])):
        logger.info("   Q%d: %r → A: %r", i + 1, q[:100], str(a)[:200])
    try:
        result = await save_user_answers(req)
        logger.info("✅ [POST /answers/save] sec_id=%s saved to DB", req.sec_id)

        # Invalidate cached section content — answers changed, regenerate fresh
        if req.sec_id:
            await cache.invalidate_section_content(req.sec_id)
            logger.info("🗑️  [CACHE DEL] section content:%s (answers updated)", req.sec_id)

        return result
    except Exception as e:
        logger.error("❌ [POST /answers/save] sec_id=%s error: %s", req.sec_id, e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Section Generation & Edit ─────────────────────────────────────────────────

@router.post("/section/generate")
async def api_generate_section(req: GenerateSectionRequest):
    """Generate section content via LLM + run quality gate check before returning."""
    logger.info(
        "📥 [POST /section/generate] sec_id=%s | section=%r | doc_type=%r | dept=%r",
        req.sec_id, req.section_name, req.doc_type, req.department,
    )
    try:
        # Check cache — if same sec_id already generated, return instantly
        if req.sec_id:
            cached = await cache.get_section_content(req.sec_id)
            if cached is not None:
                logger.info("✅ [CACHE HIT] section content:%s — skipping LLM call", req.sec_id)
                return {**cached, "cached": True}

        logger.info("🤖 [LLM] Calling generate_section_content for sec_id=%s", req.sec_id)
        result = await generate_section_content(req)

        # ── Quality gate: check generated content meets minimum standards ───────
        content    = result.get("content", "") if result else ""
        doc_type   = getattr(req, "doc_type", "") if result else ""
        passed, qc_note = check_quality(content, doc_type)
        word_count = len(content.split())
        if not passed:
            logger.warning("⚠️  [QC FAIL] sec_id=%s doc_type=%s note=%s words=%d", req.sec_id, doc_type, qc_note, word_count)
        else:
            logger.info("✅ [QC PASS] sec_id=%s | words=%d | type=%s", req.sec_id, word_count, result.get("section_type", "?"))

        # Cache the expensive LLM result (even if QC failed — let user refine)
        if req.sec_id and result:
            await cache.set_section_content(req.sec_id, result)
            logger.info("💾 [CACHE SET] section content:%s", req.sec_id)

        return {**result, "quality_passed": passed, "quality_note": qc_note if not passed else ""}
    except Exception as e:
        logger.error("❌ [POST /section/generate] sec_id=%s error: %s", req.sec_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/section/edit")
async def api_edit_section(req: EditSectionRequest):
    logger.info(
        "📥 [POST /section/edit] sec_id=%s | section=%r | instruction=%r",
        req.sec_id, req.section_name, req.edit_instruction[:120],
    )
    try:
        result = await edit_section(req)
        logger.info("✅ [POST /section/edit] sec_id=%s edit applied", req.sec_id)

        # Invalidate old cached content after edit
        if req.sec_id:
            await cache.invalidate_section_content(req.sec_id)
            logger.info("🗑️  [CACHE DEL] section content:%s (edited)", req.sec_id)

        return result
    except Exception as e:
        logger.error("❌ [POST /section/edit] sec_id=%s error: %s", req.sec_id, e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Document Save ─────────────────────────────────────────────────────────────

@router.post("/document/save")
async def api_save_document(req: SaveDocRequest):
    """
    Commit the entire generated document to the local database.
    This acts as persistent local storage before Notion publishing.
    """
    logger.info(
        "📥 [POST /document/save] doc_id=%s | doc_sec_id=%s | %d sections | full_doc_len=%d chars",
        req.doc_id, req.doc_sec_id, len(req.gen_doc_sec_dec), len(req.gen_doc_full),
    )
    try:
        gen_id = await save_generated_document(
            doc_id=req.doc_id, doc_sec_id=req.doc_sec_id, sec_id=req.sec_id,
            gen_doc_sec_dec=req.gen_doc_sec_dec, gen_doc_full=req.gen_doc_full,
        )
        logger.info("✅ [POST /document/save] Saved to DB with gen_id=%s", gen_id)
        return {"gen_id": gen_id, "saved": True}
    except Exception as e:
        logger.error("❌ [POST /document/save] doc_id=%s error: %s", req.doc_id, e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Notion ────────────────────────────────────────────────────────────────────

@router.post("/document/publish")
async def api_publish_document(req: NotionPublishRequest):
    """
    Publish the final compiled document to Notion.
    Resolves the next version number automatically and uploads images.
    """
    logger.info(
        "📥 [POST /document/publish] Publishing doc to Notion | gen_id=%s | doc_type=%r | company=%r",
        getattr(req, 'gen_id', '?'), getattr(req, 'doc_type', '?'), getattr(req, 'company_name', '?'),
    )
    try:
        result = await publish_to_notion(req)
        logger.info("✅ [POST /document/publish] Published to Notion — url=%s", result.get('notion_url', '?'))

        # Invalidate library cache so new doc appears immediately
        await cache.invalidate_notion_library()
        logger.info("🗑️  [CACHE DEL] notion_library (new doc published)")

        return result
    except Exception as e:
        logger.error("❌ [POST /document/publish] error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/library/notion")
async def api_notion_library():
    """
    Fetch the list of all published documents directly from the Notion database.
    Used to populate the Document Library view in the frontend.
    """
    try:
        # Try cache first (5-min TTL)
        cached = await cache.get_notion_library()
        if cached is not None:
            logger.info("✅ [CACHE HIT] notion_library (%d docs)", len(cached))
            return {"total": len(cached), "documents": cached, "cached": True}

        docs = await fetch_library_from_notion()

        await cache.set_notion_library(docs)
        logger.info("💾 [CACHE SET] notion_library (%d docs)", len(docs))

        return {"total": len(docs), "documents": docs, "cached": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))