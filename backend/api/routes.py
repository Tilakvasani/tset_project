"""
DocForge AI — routes.py
Full API routes for the complete document generation workflow.

Endpoints:
  GET  /departments                    → Load all departments + doc types
  GET  /sections/{doc_type}           → Load sections for a doc type
  POST /questions/generate             → Generate questions via LLM
  POST /answers/save                   → Save user answers
  POST /section/generate               → Generate section content via LLM
  POST /document/combine               → Combine all sections → full doc
  POST /section/edit                   → Edit/enhance a section via LLM
  POST /document/publish               → Publish to Notion
  GET  /document/{gen_id}             → Get a generated document
  GET  /documents                      → Get all generated documents
"""
from fastapi import APIRouter, HTTPException
from backend.core.logger import logger
from backend.services.db_service import (
    get_all_departments,
    get_sections_by_doc_type,
    get_generated_document,
    get_all_generated_documents,
)
from backend.services.generator import (
    generate_questions,
    save_user_answers,
    generate_section_content,
    combine_document,
    edit_section,
)
from backend.services.notion_service import publish_to_notion
from backend.schemas.document_schema import (
    GenerateQuestionsRequest,
    SaveAnswersRequest,
    GenerateSectionRequest,
    CombineDocumentRequest,
    EditSectionRequest,
    NotionPublishRequest,
)

router = APIRouter()


# ─── STEP 1 & 2: Load Static Data ────────────────────────────────────────────

@router.get("/departments")
async def get_departments():
    """
    Load all departments and their document types from depart table.
    Used to populate the department selector in UI.
    """
    try:
        departments = await get_all_departments()
        return {"departments": departments, "total": len(departments)}
    except Exception as e:
        logger.error(f"Failed to load departments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sections/{doc_type}")
async def get_sections(doc_type: str):
    """
    Load sections for a given document type from document_section table.
    Used to show section list after user selects doc type.
    """
    try:
        sections = await get_sections_by_doc_type(doc_type)
        if not sections:
            raise HTTPException(status_code=404, detail=f"No sections found for: {doc_type}")
        return sections
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load sections for {doc_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── STEP 3: Generate Questions (LLM) ────────────────────────────────────────

@router.post("/questions/generate")
async def api_generate_questions(req: GenerateQuestionsRequest):
    """
    LLM generates 3 questions per section based on company context.
    Saves questions to section_que_ans table.
    Returns sec_id + questions list.
    """
    try:
        logger.info(f"Generating questions: {req.section_name} | {req.doc_type}")
        result = await generate_questions(req)
        return result
    except Exception as e:
        logger.error(f"Question generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── STEP 4: Save User Answers ────────────────────────────────────────────────

@router.post("/answers/save")
async def api_save_answers(req: SaveAnswersRequest):
    """
    Save user answers to section_que_ans table.
    Updates existing row using sec_id.
    """
    try:
        logger.info(f"Saving answers: sec_id={req.sec_id}")
        result = await save_user_answers(req)
        return result
    except Exception as e:
        logger.error(f"Answer save failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── STEP 5: Generate Section Content (LLM) ──────────────────────────────────

@router.post("/section/generate")
async def api_generate_section(req: GenerateSectionRequest):
    """
    LLM generates content for one section using its Q&A answers.
    Returns section content (markdown prose).
    """
    try:
        logger.info(f"Generating section: sec_id={req.sec_id} | {req.section_name}")
        result = await generate_section_content(req)
        return result
    except Exception as e:
        logger.error(f"Section generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── STEP 6: Combine Sections → Full Document ────────────────────────────────

@router.post("/document/combine")
async def api_combine_document(req: CombineDocumentRequest):
    """
    Combine all generated sections into a full document.
    Runs a final LLM polish pass.
    Saves to gen_doc table. Returns gen_id + full document.
    """
    try:
        logger.info(f"Combining document: {req.doc_type} | {len(req.sec_ids)} sections")
        result = await combine_document(req)
        return result
    except Exception as e:
        logger.error(f"Document combine failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── STEP 7: Edit / Enhance Section ──────────────────────────────────────────

@router.post("/section/edit")
async def api_edit_section(req: EditSectionRequest):
    """
    LLM edits or enhances a specific section based on user instruction.
    Updates gen_doc table with new content.
    """
    try:
        logger.info(f"Editing section: sec_id={req.sec_id} | gen_id={req.gen_id}")
        result = await edit_section(req)
        return result
    except Exception as e:
        logger.error(f"Section edit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── STEP 8: Publish to Notion ───────────────────────────────────────────────

@router.post("/document/publish")
async def api_publish_document(req: NotionPublishRequest):
    """
    Publish the final document to Notion.
    Returns Notion page URL.
    """
    try:
        logger.info(f"Publishing to Notion: gen_id={req.gen_id}")
        result = await publish_to_notion(req)
        return result
    except Exception as e:
        logger.error(f"Notion publish failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Fetch Documents ──────────────────────────────────────────────────────────

@router.get("/document/{gen_id}")
async def api_get_document(gen_id: int):
    """Fetch a single generated document by gen_id."""
    try:
        doc = await get_generated_document(gen_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document not found: gen_id={gen_id}")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def api_get_all_documents(doc_id: int = None):
    """Fetch all generated documents. Optionally filter by department doc_id."""
    try:
        docs = await get_all_generated_documents(doc_id=doc_id)
        return {"total": len(docs), "documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))