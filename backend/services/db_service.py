"""
backend/services/db_service.py

Saves to PostgreSQL:
  - documents       → 1 row (full doc + metadata)
  - document_sections → 1 row (all 7 sections, 14 answers, flat columns)

Install:  pip install asyncpg
.env:     DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/docforge_db
"""

import asyncpg
from typing import Optional
from backend.core.config import settings
from backend.core.logger import logger


async def get_connection() -> asyncpg.Connection:
    return await asyncpg.connect(settings.DATABASE_URL)


async def save_document_with_sections(
    doc_id: str,
    title: str,
    industry: str,
    department: str,
    doc_type: str,
    version: str,
    content: str,
    tags: list,
    created_by: str,
    answers: dict,          # gen_answers dict from Streamlit session_state
    template_id: str = None,
) -> str:
    """
    Saves 1 row to documents + 1 row to document_sections.
    answers keys must match generator_form.py session_state keys:
        s1: doc_title, doc_version
        s2: purpose_main, purpose_problem
        s3: scope_applies, scope_exclusions
        s4: resp_implement, resp_maintain
        s5: proc_steps, proc_tools
        s6: comp_regs, comp_risks
        s7: conc_outcome, conc_review
    """
    word_count = len(content.split())
    conn = await get_connection()

    try:
        async with conn.transaction():

            # ── INSERT into documents ────────────────────────────
            await conn.execute("""
                INSERT INTO documents (
                    id, title, industry, department, doc_type,
                    version, content, word_count, tags,
                    created_by, status, published, template_id
                ) VALUES (
                    $1, $2, $3, $4, $5,
                    $6, $7, $8, $9::text[],
                    $10, 'Generated', FALSE, $11
                )
            """,
                doc_id, title, industry, department, doc_type,
                version, content, word_count, tags,
                created_by, template_id
            )

            # ── INSERT into document_sections (ONE flat row) ─────
            await conn.execute("""
                INSERT INTO document_sections (
                    document_id,

                    s1_answer_1, s1_answer_2,
                    s2_answer_1, s2_answer_2,
                    s3_answer_1, s3_answer_2,
                    s4_answer_1, s4_answer_2,
                    s5_answer_1, s5_answer_2,
                    s6_answer_1, s6_answer_2,
                    s7_answer_1, s7_answer_2
                ) VALUES (
                    $1,
                    $2,  $3,
                    $4,  $5,
                    $6,  $7,
                    $8,  $9,
                    $10, $11,
                    $12, $13,
                    $14, $15
                )
            """,
                doc_id,
                answers.get("doc_title", ""),        answers.get("doc_version", ""),
                answers.get("purpose_main", ""),     answers.get("purpose_problem", ""),
                answers.get("scope_applies", ""),    answers.get("scope_exclusions", ""),
                answers.get("resp_implement", ""),   answers.get("resp_maintain", ""),
                answers.get("proc_steps", ""),       answers.get("proc_tools", ""),
                answers.get("comp_regs", ""),        answers.get("comp_risks", ""),
                answers.get("conc_outcome", ""),     answers.get("conc_review", ""),
            )

        logger.info(f"✅ Saved doc {doc_id} to PostgreSQL (documents + document_sections)")
        return doc_id

    except Exception as e:
        logger.error(f"❌ DB save failed: {e}")
        raise
    finally:
        await conn.close()


async def update_notion_url(doc_id: str, notion_url: str, notion_page_id: str):
    """Called after Notion publish — stamps notion_url + published=TRUE."""
    conn = await get_connection()
    try:
        await conn.execute("""
            UPDATE documents
            SET notion_url     = $1,
                notion_page_id = $2,
                published      = TRUE
            WHERE id = $3
        """, notion_url, notion_page_id, doc_id)
        logger.info(f"✅ Updated notion_url for doc {doc_id}")
    finally:
        await conn.close()


async def get_document_with_sections(doc_id: str) -> Optional[dict]:
    """Fetch one document + its sections via the v_documents_full view."""
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "SELECT * FROM v_documents_full WHERE id = $1", doc_id
        )
        return dict(row) if row else None
    finally:
        await conn.close()


async def get_all_documents(
    department: str = None,
    doc_type: str = None,
    status: str = None,
    limit: int = 50,
) -> list:
    """Fetch all documents with optional filters."""
    conn = await get_connection()
    try:
        conditions = []
        params = []
        i = 1

        if department:
            conditions.append(f"department = ${i}"); params.append(department); i += 1
        if doc_type:
            conditions.append(f"doc_type = ${i}"); params.append(doc_type); i += 1
        if status:
            conditions.append(f"status = ${i}"); params.append(status); i += 1

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        params.append(limit)

        rows = await conn.fetch(f"""
            SELECT id, doc_number, title, department, doc_type,
                   version, word_count, tags, created_by,
                   status, published, notion_url, created_at
            FROM documents
            {where}
            ORDER BY created_at DESC
            LIMIT ${i}
        """, *params)

        return [dict(r) for r in rows]
    finally:
        await conn.close()
