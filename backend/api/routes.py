"""
DocForge AI — routes.py
All API endpoints for the full workflow.
"""
import json
import subprocess
import tempfile
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

from backend.core.logger import logger
from backend.services.db_service import (
    get_all_departments, get_sections_by_doc_type,
    get_generated_document, get_all_generated_documents,
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

router = APIRouter()


# ── Request schemas ────────────────────────────────────────────────────────────

class SaveDocRequest(BaseModel):
    doc_id: int
    doc_sec_id: int
    sec_id: int
    gen_doc_sec_dec: List[str]
    gen_doc_full: str          # PLAIN TEXT


class DownloadDocxRequest(BaseModel):
    doc_type: str
    department: str
    company_name: str
    industry: str
    region: str
    sections: List[dict]       # [{"name": ..., "content": ...}]


# ── Static data ────────────────────────────────────────────────────────────────

@router.get("/departments")
async def get_departments():
    try:
        depts = await get_all_departments()
        return {"departments": depts, "total": len(depts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sections/{doc_type}")
async def get_sections(doc_type: str):
    decoded = doc_type.replace("%2F", "/").replace("%28", "(").replace("%29", ")")
    try:
        sections = await get_sections_by_doc_type(decoded)
        if not sections:
            raise HTTPException(status_code=404, detail=f"No sections for: {decoded}")
        return sections
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Questions ──────────────────────────────────────────────────────────────────

@router.post("/questions/generate")
async def api_generate_questions(req: GenerateQuestionsRequest):
    try:
        return await generate_questions(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Answers ────────────────────────────────────────────────────────────────────

@router.post("/answers/save")
async def api_save_answers(req: SaveAnswersRequest):
    try:
        return await save_user_answers(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Section content ────────────────────────────────────────────────────────────

@router.post("/section/generate")
async def api_generate_section(req: GenerateSectionRequest):
    try:
        return await generate_section_content(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/section/edit")
async def api_edit_section(req: EditSectionRequest):
    try:
        return await edit_section(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Save full document to gen_doc ──────────────────────────────────────────────

@router.post("/document/save")
async def api_save_document(req: SaveDocRequest):
    try:
        gen_id = await save_generated_document(
            doc_id=req.doc_id,
            doc_sec_id=req.doc_sec_id,
            sec_id=req.sec_id,
            gen_doc_sec_dec=req.gen_doc_sec_dec,
            gen_doc_full=req.gen_doc_full,
        )
        logger.info(f"Document saved: gen_id={gen_id}")
        return {"gen_id": gen_id, "saved": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Publish to Notion ──────────────────────────────────────────────────────────

@router.post("/document/publish")
async def api_publish_document(req: NotionPublishRequest):
    try:
        return await publish_to_notion(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Notion Library ─────────────────────────────────────────────────────────────

@router.get("/library/notion")
async def api_notion_library():
    """Fetch all published docs from Notion database for the Library view."""
    try:
        docs = await fetch_library_from_notion()
        return {"total": len(docs), "documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Generate DOCX file ─────────────────────────────────────────────────────────

@router.post("/document/download/docx")
async def api_download_docx(req: DownloadDocxRequest):
    """
    Generate a .docx file from section data and return it as a file download.
    Uses generate_docx.js via subprocess.
    """
    try:
        # Write input JSON to temp file
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump({
                "doc_type":     req.doc_type,
                "department":   req.department,
                "company_name": req.company_name,
                "industry":     req.industry,
                "region":       req.region,
                "sections":     req.sections,
            }, f)
            input_path = f.name

        output_path = input_path.replace('.json', '.docx')

        # Find generate_docx.js (located next to this file or in project root)
        script_candidates = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'generate_docx.js'),
            os.path.join(os.path.dirname(__file__), '..', 'generate_docx.js'),
            'generate_docx.js',
        ]
        script_path = next(
            (p for p in script_candidates if os.path.exists(p)),
            'generate_docx.js'
        )

        result = subprocess.run(
            ['node', script_path, input_path, output_path],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            raise Exception(f"DOCX generation failed: {result.stderr}")

        safe_name = req.doc_type.replace(" ", "_").replace("/", "-")
        return FileResponse(
            path=output_path,
            filename=f"{safe_name}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    except Exception as e:
        logger.error(f"DOCX generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.unlink(input_path)
        except Exception:
            pass


# ── Fetch documents from DB ────────────────────────────────────────────────────

@router.get("/document/{gen_id}")
async def api_get_document(gen_id: int):
    try:
        doc = await get_generated_document(gen_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"gen_id={gen_id} not found")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def api_get_all_documents(doc_id: int = None):
    try:
        docs = await get_all_generated_documents(doc_id=doc_id)
        return {"total": len(docs), "documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))