"""
DocForge AI — generator.py
- Industry-standard section lengths per doc type
- Plain text output only (no markdown)
- Smart question count 0-3
- Handles empty / not-answered / skipped gracefully
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.core.config import settings
from backend.core.logger import logger
from backend.services.db_service import (
    save_questions, save_answers, get_qa_by_sec_id,
    save_generated_document, update_section_content, get_generated_document,
)
from backend.services.document_utils import markdown_to_plain_text, get_words_per_section
from backend.schemas.document_schema import (
    GenerateQuestionsRequest, GenerateQuestionsResponse,
    SaveAnswersRequest, SaveAnswersResponse,
    GenerateSectionRequest, GenerateSectionResponse,
    EditSectionRequest, EditSectionResponse,
)


def get_llm(temperature: float = 0.7) -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        api_key=settings.GROQ_API_KEY
    )


# ─── Smart Question Generation (0–3) ─────────────────────────────────────────

SMART_QUESTION_PROMPT = PromptTemplate(
    input_variables=["section_name", "doc_type", "department",
                     "company_name", "industry", "company_size", "region"],
    template="""You are an expert enterprise documentation specialist.

Decide how many questions (0, 1, 2, or 3) are needed to fill this document section, then write exactly that many.

Document Type: {doc_type}
Department: {department}
Section: {section_name}
Company: {company_name} | Industry: {industry}

Decision rules:
- 0 questions: Purely structural — signature blocks, document title, date stamps, logo, version stamps, header metadata, authorized signatory placeholders. Respond: NONE
- 1 question: Simple single-value sections — one date, one name, one role
- 2 questions: Needs 2 distinct pieces of context
- 3 questions: Complex section needing multiple details (maximum allowed)

Output rules:
- If 0 questions: respond with exactly the word NONE
- Otherwise: one question per line, no numbering, no extra text
- Questions must be specific and answerable by a business professional

Respond now:"""
)


async def generate_questions(req: GenerateQuestionsRequest) -> GenerateQuestionsResponse:
    ctx = req.company_context or {}
    chain = SMART_QUESTION_PROMPT | get_llm(0.4) | StrOutputParser()

    raw = chain.invoke({
        "section_name": req.section_name, "doc_type": req.doc_type,
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

    logger.info(f"Questions: {len(questions)} for '{req.section_name}' → sec_id={sec_id}")
    return GenerateQuestionsResponse(
        sec_id=sec_id, doc_sec_id=req.doc_sec_id, doc_id=req.doc_id,
        section_name=req.section_name, questions=questions
    )


# ─── Save Answers ─────────────────────────────────────────────────────────────

async def save_user_answers(req: SaveAnswersRequest) -> SaveAnswersResponse:
    await save_answers(
        sec_id=req.sec_id, questions=req.questions,
        answers=req.answers, section_name=req.section_name
    )
    return SaveAnswersResponse(sec_id=req.sec_id, section_name=req.section_name, saved=True)


# ─── Generate Section Content — PLAIN TEXT, calibrated length ─────────────────

SECTION_GEN_PROMPT = PromptTemplate(
    input_variables=["doc_type", "department", "section_name", "company_name",
                     "industry", "company_size", "region", "qa_block", "target_words"],
    template="""You are a professional enterprise documentation writer.

Write content for the "{section_name}" section of a {doc_type}.

Company: {company_name} | Department: {department} | Industry: {industry} | Region: {region}

User context:
{qa_block}

STRICT FORMATTING RULES — you MUST follow these exactly:
1. Write approximately {target_words} words — not more, not less
2. PLAIN TEXT ONLY — absolutely zero markdown
3. No asterisks (*), no hash symbols (#), no backticks (`), no underscores for formatting
4. No bold markers, no italic markers, no horizontal rules
5. Write in regular paragraphs separated by blank lines
6. For any lists, use "1. Item" for numbered or "- Item" for plain dash bullets
7. "not answered" means: write realistic professional placeholder content
8. Do NOT include a section heading — content only
9. Professional enterprise tone for {department} department
10. Do NOT repeat any questions

Write the plain text section content now:"""
)


async def generate_section_content(req: GenerateSectionRequest) -> GenerateSectionResponse:
    qa_row = await get_qa_by_sec_id(req.sec_id)
    if not qa_row:
        raise ValueError(f"No Q&A found for sec_id={req.sec_id}")

    qa_data   = qa_row["doc_sec_que_ans"]
    questions = qa_data.get("questions", [])
    answers   = qa_data.get("answers",   [])

    if not questions:
        qa_block = "No specific questions — write professional standard content for this section type."
    else:
        lines = []
        for q, a in zip(questions, answers):
            lines += [f"Q: {q}", f"A: {a}", ""]
        qa_block = "\n".join(lines)

    target_words = get_words_per_section(req.doc_type, req.num_sections or 10)
    ctx   = req.company_context or {}
    chain = SECTION_GEN_PROMPT | get_llm(0.7) | StrOutputParser()

    raw = chain.invoke({
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

    # Always strip any markdown the LLM sneaks in
    clean = markdown_to_plain_text(raw.strip())

    return GenerateSectionResponse(
        sec_id=req.sec_id, section_name=req.section_name, content=clean
    )


# ─── Edit Section — PLAIN TEXT output ─────────────────────────────────────────

EDIT_PROMPT = PromptTemplate(
    input_variables=["section_name", "current_content", "edit_instruction"],
    template="""Professional enterprise document editor.

Section: {section_name}
Current Content:
{current_content}

Instruction: {edit_instruction}

Apply the instruction. Professional tone.
PLAIN TEXT ONLY — no markdown, no asterisks, no # symbols.
Return ONLY the updated section content:"""
)


async def edit_section(req: EditSectionRequest) -> EditSectionResponse:
    chain  = EDIT_PROMPT | get_llm(0.6) | StrOutputParser()
    raw    = chain.invoke({
        "section_name":     req.section_name,
        "current_content":  req.current_content,
        "edit_instruction": req.edit_instruction,
    }).strip()

    updated = markdown_to_plain_text(raw)

    gen_doc = await get_generated_document(req.gen_id)
    if gen_doc:
        full_doc = gen_doc.get("gen_doc_full", "").replace(req.current_content, updated)
        await update_section_content(req.gen_id, gen_doc.get("gen_doc_sec_dec", []), full_doc)

    return EditSectionResponse(
        sec_id=req.sec_id, section_name=req.section_name, updated_content=updated
    )