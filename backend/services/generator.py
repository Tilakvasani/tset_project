"""
DocForge AI — generator.py  v5.1
- Text sections: LLM generates 0-3 questions, user answers, LLM writes plain text
- Table sections: LLM generates 1-3 questions about the table data,
  user answers in normal text areas, LLM builds a pipe-format table from answers
- No special column/row UI — same answer flow for all sections
"""
import re
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.core.config import settings
from backend.core.logger import logger
from backend.services.db_service import (
    save_questions, save_answers, get_qa_by_sec_id,
    update_section_content, get_generated_document,
)
from backend.services.document_utils import (
    markdown_to_plain_text, get_words_per_section, SECTIONS_NEEDING_TABLES
)
from backend.schemas.document_schema import (
    GenerateQuestionsRequest, SaveAnswersRequest,
    GenerateSectionRequest, EditSectionRequest,
)


def get_llm(temperature: float = 0.7) -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=settings.AZURE_LLM_ENDPOINT,
        api_key=settings.AZURE_OPENAI_LLM_KEY,
        azure_deployment=settings.AZURE_LLM_DEPLOYMENT_41_MINI,
        api_version="2024-12-01-preview",
        temperature=temperature,
    )


def _needs_table(doc_type: str, section_name: str) -> bool:
    key = f"{doc_type}|{section_name}".lower()
    return any(p.lower() in key for p in SECTIONS_NEEDING_TABLES)


# ─── Question Generation ──────────────────────────────────────────────────────

TEXT_QUESTIONS_PROMPT = PromptTemplate(
    input_variables=["section_name", "doc_type", "department",
                     "company_name", "industry", "company_size", "region"],
    template="""You are an expert enterprise documentation specialist.

Decide how many questions (0, 1, 2, or 3) are needed to fill this section, then write exactly that many.

Document Type: {doc_type}
Department: {department}
Section: {section_name}
Company: {company_name} | Industry: {industry}

Rules:
- 0 questions: Purely structural — signature blocks, date stamps, version stamps. Respond: NONE
- 1 question: Simple single-value — one date, one name, one role
- 2 questions: Needs 2 distinct pieces of context
- 3 questions: Complex section needing multiple details (maximum)

Output:
- If 0 questions: respond NONE
- Otherwise: one question per line, no numbering, no extra text

Respond now:"""
)

TABLE_QUESTIONS_PROMPT = PromptTemplate(
    input_variables=["section_name", "doc_type", "department", "company_name", "industry"],
    template="""You are an expert enterprise documentation specialist.

This section will contain a data table. Write 1-3 questions to collect the table data from the user.

Document Type: {doc_type}
Department: {department}
Section: {section_name}
Company: {company_name} | Industry: {industry}

Rules:
- Ask for the actual row data that should go in the table
- Questions should be clear and specific about what data to provide
- Example for "Commission Earned per Deal":
  "List each deal with: deal name, amount, commission rate, and commission earned (one deal per line)"
- Maximum 3 questions
- One question per line, no numbering, no extra text

Respond now:"""
)


async def generate_questions(req: GenerateQuestionsRequest) -> dict:
    ctx      = req.company_context or {}
    is_table = _needs_table(req.doc_type, req.section_name)

    if is_table:
        chain = TABLE_QUESTIONS_PROMPT | get_llm(0.3) | StrOutputParser()
        raw   = chain.invoke({
            "section_name": req.section_name,
            "doc_type":     req.doc_type,
            "department":   req.department,
            "company_name": ctx.get("company_name", "the company"),
            "industry":     ctx.get("industry", "general"),
        }).strip()
    else:
        chain = TEXT_QUESTIONS_PROMPT | get_llm(0.3) | StrOutputParser()
        raw   = chain.invoke({
            "section_name": req.section_name,
            "doc_type":     req.doc_type,
            "department":   req.department,
            "company_name": ctx.get("company_name", "the company"),
            "industry":     ctx.get("industry", "general"),
            "company_size": ctx.get("company_size", "not specified"),
            "region":       ctx.get("region", "not specified"),
        }).strip()

    questions = [] if (not raw or raw.upper() == "NONE") else [
        q.strip() for q in raw.split("\n") if q.strip()
    ][:3]

    sec_id = await save_questions(
        doc_sec_id=req.doc_sec_id, doc_id=req.doc_id,
        section_name=req.section_name, questions=questions
    )
    logger.info(f"{'Table' if is_table else 'Text'} questions: {len(questions)} for '{req.section_name}'")
    return {
        "sec_id":       sec_id,
        "doc_sec_id":   req.doc_sec_id,
        "doc_id":       req.doc_id,
        "section_name": req.section_name,
        "questions":    questions,
        "is_table":     is_table,
    }


# ─── Save Answers ─────────────────────────────────────────────────────────────

async def save_user_answers(req: SaveAnswersRequest) -> dict:
    await save_answers(
        sec_id=req.sec_id, questions=req.questions,
        answers=req.answers, section_name=req.section_name
    )
    return {"sec_id": req.sec_id, "section_name": req.section_name, "saved": True}


# ─── Section Content Prompts ──────────────────────────────────────────────────

SECTION_TEXT_PROMPT = PromptTemplate(
    input_variables=["doc_type", "department", "section_name", "company_name",
                     "industry", "company_size", "region", "qa_block", "target_words"],
    template="""You are a professional enterprise documentation writer.

Write the "{section_name}" section of a {doc_type}.

Company: {company_name} | Dept: {department} | Industry: {industry} | Region: {region}

User answers:
{qa_block}

STRICT RULES:
1. Write EXACTLY {target_words} words — hard limit, do NOT exceed
2. PLAIN TEXT ONLY — zero markdown, no asterisks, no # symbols, no backticks
3. Regular paragraphs separated by blank lines
4. Lists: use "1. Item" or "- Item" only
5. "not answered" = write realistic professional placeholder content
6. No section heading in output
7. Professional {department} department tone

Write now:"""
)

SECTION_TABLE_PROMPT = PromptTemplate(
    input_variables=["doc_type", "department", "section_name", "company_name",
                     "industry", "region", "qa_block"],
    template="""You are a professional enterprise documentation writer.

Write the "{section_name}" section of a {doc_type}. This section MUST contain a data table.

Company: {company_name} | Dept: {department} | Industry: {industry} | Region: {region}

User-provided data:
{qa_block}

OUTPUT FORMAT — follow this EXACTLY:
1. One sentence of plain text introduction (no markdown)
2. A blank line
3. A pipe-format table using the user's data:

   Column1 | Column2 | Column3
   ------- | ------- | -------
   value1  | value2  | value3
   value2  | value2  | value3

STRICT RULES:
- Use the user's data to populate the table rows
- If user said "not answered" or gave no data, create an empty table with appropriate columns for {section_name} of a {doc_type}
- Table columns must be industry-standard for this section type
- NO markdown outside the table — no **, no ##, no backticks
- The intro sentence goes BEFORE the table, never inside a cell
- No section heading

Write now:"""
)


async def generate_section_content(req: GenerateSectionRequest) -> dict:
    qa_row = await get_qa_by_sec_id(req.sec_id)
    if not qa_row:
        raise ValueError(f"No Q&A found for sec_id={req.sec_id}")

    qa_data   = qa_row["doc_sec_que_ans"]
    questions = qa_data.get("questions", [])
    answers   = qa_data.get("answers",   [])
    is_table  = _needs_table(req.doc_type, req.section_name)
    ctx       = req.company_context or {}

    qa_block = (
        "No specific input — use professional placeholder content."
        if not questions else
        "\n".join(f"Q: {q}\nA: {a}\n" for q, a in zip(questions, answers))
    )

    if is_table:
        chain = SECTION_TABLE_PROMPT | get_llm(0.5) | StrOutputParser()
        raw   = chain.invoke({
            "doc_type":     req.doc_type,
            "department":   req.department,
            "section_name": req.section_name,
            "company_name": ctx.get("company_name", "the company"),
            "industry":     ctx.get("industry", "general"),
            "region":       ctx.get("region", "not specified"),
            "qa_block":     qa_block,
        })
        clean = _clean_preserve_tables(raw.strip())
        logger.info(f"Table section '{req.section_name}' generated")

    else:
        target_words = get_words_per_section(req.doc_type, req.num_sections or 10)
        chain = SECTION_TEXT_PROMPT | get_llm(0.7) | StrOutputParser()
        raw   = chain.invoke({
            "doc_type":     req.doc_type,
            "department":   req.department,
            "section_name": req.section_name,
            "company_name": ctx.get("company_name", "the company"),
            "industry":     ctx.get("industry", "general"),
            "company_size": ctx.get("company_size", "not specified"),
            "region":       ctx.get("region", "not specified"),
            "qa_block":     qa_block,
            "target_words": target_words,
        })
        clean = _clean_preserve_tables(raw.strip())

        # Hard word limit
        words = clean.split()
        if len(words) > target_words * 1.2:
            truncated   = " ".join(words[:target_words])
            last_period = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
            clean = truncated[:last_period + 1].strip() if last_period > len(truncated) * 0.6 else truncated

        logger.info(f"Text section '{req.section_name}' — {len(clean.split())} words")

    return {"sec_id": req.sec_id, "section_name": req.section_name, "content": clean}


def _clean_preserve_tables(text: str) -> str:
    lines  = text.split('\n')
    result = [line.rstrip() if '|' in line else markdown_to_plain_text(line) for line in lines]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(result)).strip()


# ─── Edit Section ─────────────────────────────────────────────────────────────

EDIT_PROMPT = PromptTemplate(
    input_variables=["section_name", "current_content", "edit_instruction"],
    template="""Professional enterprise document editor.

Section: {section_name}
Current Content:
{current_content}

Instruction: {edit_instruction}

PLAIN TEXT ONLY — no markdown, no asterisks, no # symbols.
If a pipe-format table exists, keep it exactly in pipe format.
Return ONLY the updated content:"""
)


async def edit_section(req: EditSectionRequest) -> dict:
    chain   = EDIT_PROMPT | get_llm(0.6) | StrOutputParser()
    raw     = chain.invoke({
        "section_name":     req.section_name,
        "current_content":  req.current_content,
        "edit_instruction": req.edit_instruction,
    }).strip()

    updated = _clean_preserve_tables(raw)

    gen_doc = await get_generated_document(req.gen_id)
    if gen_doc:
        full_doc = gen_doc.get("gen_doc_full", "").replace(req.current_content, updated)
        await update_section_content(req.gen_id, gen_doc.get("gen_doc_sec_dec", []), full_doc)

    return {"sec_id": req.sec_id, "section_name": req.section_name, "updated_content": updated}