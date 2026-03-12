"""
DocForge AI — generator.py
Full workflow implementation:
  1. generate_questions()     → LLM generates questions per section
  2. generate_section()       → LLM generates content using Q&A
  3. combine_document()       → Assembles all sections into full doc
  4. edit_section()           → LLM edits/enhances a specific section
"""
import json
from typing import List, Dict, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.core.config import settings
from backend.core.logger import logger
from backend.services.db_service import (
    save_questions,
    save_answers,
    get_qa_by_sec_id,
    get_all_qa_for_document,
    save_generated_document,
    update_section_content,
    get_generated_document,
)
from backend.schemas.document_schema import (
    GenerateQuestionsRequest, GenerateQuestionsResponse,
    SaveAnswersRequest, SaveAnswersResponse,
    GenerateSectionRequest, GenerateSectionResponse,
    CombineDocumentRequest, CombineDocumentResponse,
    EditSectionRequest, EditSectionResponse,
)


# ─── LLM Setup ───────────────────────────────────────────────────────────────

def get_llm(temperature: float = 0.7) -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        api_key=settings.GROQ_API_KEY
    )


# ─── STEP 3: Generate Questions (LLM) ────────────────────────────────────────

QUESTION_GEN_PROMPT = PromptTemplate(
    input_variables=[
        "section_name", "doc_type", "department",
        "company_name", "industry", "company_size", "region"
    ],
    template="""You are an expert enterprise documentation specialist.

Your task is to generate EXACTLY 3 clear, specific questions to help a user fill in a document section.

Document Type: {doc_type}
Department: {department}
Section: {section_name}
Company: {company_name}
Industry: {industry}
Company Size: {company_size}
Region: {region}

Rules:
- Generate exactly 3 questions
- Questions must be specific to the section and relevant to the company context
- Each question should gather distinct, non-overlapping information
- Questions should be practical and answerable by a typical business user
- Do NOT number the questions
- Return ONLY the questions, one per line, nothing else

Generate 3 questions now:"""
)

async def generate_questions(req: GenerateQuestionsRequest) -> GenerateQuestionsResponse:
    """
    Step 3: LLM generates 3 questions per section.
    Saves questions to section_que_ans table.
    """
    logger.info(f"Generating questions: {req.section_name} | {req.doc_type}")

    ctx = req.company_context or {}
    llm = get_llm(temperature=0.5)
    parser = StrOutputParser()
    chain = QUESTION_GEN_PROMPT | llm | parser

    raw = chain.invoke({
        "section_name": req.section_name,
        "doc_type": req.doc_type,
        "department": req.department,
        "company_name": ctx.get("company_name", "the company"),
        "industry": ctx.get("industry", "general"),
        "company_size": ctx.get("company_size", "not specified"),
        "region": ctx.get("region", "not specified"),
    })

    # Parse questions — one per line, strip empty
    questions = [q.strip() for q in raw.strip().split("\n") if q.strip()][:3]

    # Ensure exactly 3 questions
    while len(questions) < 3:
        questions.append(f"Please provide additional details for {req.section_name}.")

    # Save to DB
    sec_id = await save_questions(
        doc_sec_id=req.doc_sec_id,
        doc_id=req.doc_id,
        section_name=req.section_name,
        questions=questions
    )

    logger.info(f"Questions saved: sec_id={sec_id}")
    return GenerateQuestionsResponse(
        sec_id=sec_id,
        doc_sec_id=req.doc_sec_id,
        doc_id=req.doc_id,
        section_name=req.section_name,
        questions=questions
    )


# ─── STEP 4: Save User Answers ────────────────────────────────────────────────

async def save_user_answers(req: SaveAnswersRequest) -> SaveAnswersResponse:
    """
    Step 4: Save user's answers to section_que_ans table.
    """
    logger.info(f"Saving answers: sec_id={req.sec_id}, section={req.section_name}")

    await save_answers(
        sec_id=req.sec_id,
        questions=req.questions,
        answers=req.answers,
        section_name=req.section_name
    )

    return SaveAnswersResponse(
        sec_id=req.sec_id,
        section_name=req.section_name,
        saved=True
    )


# ─── STEP 5: Generate Section Content (LLM) ──────────────────────────────────

SECTION_GEN_PROMPT = PromptTemplate(
    input_variables=[
        "doc_type", "department", "section_name",
        "company_name", "industry", "company_size", "region",
        "qa_block"
    ],
    template="""You are a professional enterprise documentation writer.

Write the content for ONE document section based on the provided Q&A answers.

Document Type: {doc_type}
Department: {department}
Section: {section_name}
Company: {company_name}
Industry: {industry}
Company Size: {company_size}
Region: {region}

Q&A Answers for this section:
{qa_block}

Instructions:
- Write 150 to 300 words of professional prose for this section
- Use the answers to create specific, detailed content — do NOT be generic
- Use markdown formatting (bold, bullet points where appropriate)
- Professional enterprise tone throughout
- Do NOT include a section header — just write the content
- Do NOT repeat the questions

Write the section content now:"""
)

async def generate_section_content(req: GenerateSectionRequest) -> GenerateSectionResponse:
    """
    Step 5: LLM generates content for one section using Q&A answers.
    """
    logger.info(f"Generating section content: sec_id={req.sec_id}, section={req.section_name}")

    # Fetch Q&A from DB
    qa_row = await get_qa_by_sec_id(req.sec_id)
    if not qa_row:
        raise ValueError(f"No Q&A found for sec_id={req.sec_id}")

    qa_data = qa_row["doc_sec_que_ans"]
    questions = qa_data.get("questions", [])
    answers = qa_data.get("answers", [])

    # Build Q&A block for prompt
    qa_lines = []
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        qa_lines.append(f"Q{i}: {q}")
        qa_lines.append(f"A{i}: {a if a else 'Not provided'}")
        qa_lines.append("")
    qa_block = "\n".join(qa_lines)

    ctx = req.company_context or {}
    llm = get_llm(temperature=0.7)
    parser = StrOutputParser()
    chain = SECTION_GEN_PROMPT | llm | parser

    content = chain.invoke({
        "doc_type": req.doc_type,
        "department": req.department,
        "section_name": req.section_name,
        "company_name": ctx.get("company_name", "the company"),
        "industry": ctx.get("industry", "general"),
        "company_size": ctx.get("company_size", "not specified"),
        "region": ctx.get("region", "not specified"),
        "qa_block": qa_block,
    })

    logger.info(f"Section content generated: sec_id={req.sec_id}")
    return GenerateSectionResponse(
        sec_id=req.sec_id,
        section_name=req.section_name,
        content=content.strip()
    )


# ─── STEP 6: Combine Sections → Full Document ────────────────────────────────

ASSEMBLY_PROMPT = PromptTemplate(
    input_variables=["doc_type", "company_name", "combined_sections"],
    template="""You are a professional document editor.

The following is a {doc_type} for {company_name}, assembled from individually written sections.

Your task:
1. Fix any terminology inconsistencies across sections
2. Improve transitions between sections for better flow
3. Do NOT add new content or change the meaning
4. Return the complete polished document in markdown format
5. Keep all section headers (## Section Name) exactly as they are

Document:
{combined_sections}

Return the polished document now:"""
)

async def combine_document(req: CombineDocumentRequest) -> CombineDocumentResponse:
    """
    Step 6: Fetch all generated section contents, combine into full document.
    Runs a final assembly pass through LLM for polish.
    Saves to gen_doc table.
    """
    logger.info(f"Combining document: doc_type={req.doc_type}, sections={len(req.sec_ids)}")

    # Collect all section contents from DB
    section_contents = []
    section_summaries = []

    for sec_id in req.sec_ids:
        qa_row = await get_qa_by_sec_id(sec_id)
        if not qa_row:
            logger.warning(f"Missing Q&A for sec_id={sec_id}, skipping")
            continue

        qa_data = qa_row["doc_sec_que_ans"]
        section_name = qa_data.get("section_name", f"Section {sec_id}")

        # Get generated content stored in session state (passed via sec_ids context)
        # In production this would be stored in a generated_sections table
        # For now we re-generate if needed or use what was passed
        content = qa_data.get("generated_content", "")
        if content:
            section_summaries.append(f"## {section_name}\n\n{content}")
            section_contents.append(content)

    combined_raw = "\n\n---\n\n".join(section_summaries)

    # Auto-generate header sections
    header = f"""# {req.doc_type}

**Organization:** {req.company_context.get('company_name', 'Company Name')}
**Department:** {req.department}
**Industry:** {req.company_context.get('industry', 'N/A')}
**Region:** {req.company_context.get('region', 'N/A')}
**Document Version:** v1.0
**Classification:** Internal Use Only
**Generated by:** DocForge AI

---

"""

    full_draft = header + combined_raw

    # Assembly polish pass
    ctx = req.company_context or {}
    llm = get_llm(temperature=0.3)
    parser = StrOutputParser()
    chain = ASSEMBLY_PROMPT | llm | parser

    try:
        final_doc = chain.invoke({
            "doc_type": req.doc_type,
            "company_name": ctx.get("company_name", "the company"),
            "combined_sections": full_draft,
        })
    except Exception as e:
        logger.warning(f"Assembly LLM pass failed, using raw: {e}")
        final_doc = full_draft

    # Use the last sec_id as the primary FK reference
    primary_sec_id = req.sec_ids[-1] if req.sec_ids else 0

    # Save to gen_doc
    gen_id = await save_generated_document(
        doc_id=req.doc_id,
        doc_sec_id=req.doc_sec_id,
        sec_id=primary_sec_id,
        gen_doc_sec_dec=section_contents,
        gen_doc_full=final_doc
    )

    logger.info(f"Full document saved: gen_id={gen_id}")

    return CombineDocumentResponse(
        gen_id=gen_id,
        doc_id=req.doc_id,
        doc_sec_id=req.doc_sec_id,
        doc_type=req.doc_type,
        department=req.department,
        gen_doc_sec_dec=section_contents,
        gen_doc_full=final_doc
    )


# ─── STEP 7: Edit / Enhance a Section (LLM) ──────────────────────────────────

EDIT_PROMPT = PromptTemplate(
    input_variables=["section_name", "current_content", "edit_instruction"],
    template="""You are a professional enterprise document editor.

Section: {section_name}

Current Content:
{current_content}

Edit Instruction from User:
{edit_instruction}

Rules:
- Apply the edit instruction carefully
- Maintain professional enterprise tone
- Keep markdown formatting
- Do NOT add a section header
- Return ONLY the updated section content

Write the updated section content now:"""
)

async def edit_section(req: EditSectionRequest) -> EditSectionResponse:
    """
    Step 7: Edit or enhance a specific section using LLM.
    Updates the gen_doc table with new content.
    """
    logger.info(f"Editing section: sec_id={req.sec_id}, instruction={req.edit_instruction[:50]}")

    llm = get_llm(temperature=0.6)
    parser = StrOutputParser()
    chain = EDIT_PROMPT | llm | parser

    updated_content = chain.invoke({
        "section_name": req.section_name,
        "current_content": req.current_content,
        "edit_instruction": req.edit_instruction,
    })

    # Fetch existing gen_doc to rebuild full doc
    gen_doc = await get_generated_document(req.gen_id)
    if gen_doc:
        # Replace the section content in gen_doc_sec_dec
        sections = gen_doc.get("gen_doc_sec_dec", [])
        # Update full doc by replacing old section content with new
        full_doc = gen_doc.get("gen_doc_full", "")
        full_doc = full_doc.replace(req.current_content, updated_content.strip())

        # Update DB
        await update_section_content(
            gen_id=req.gen_id,
            updated_sections=sections,
            full_doc=full_doc
        )

    logger.info(f"Section edited: sec_id={req.sec_id}")
    return EditSectionResponse(
        sec_id=req.sec_id,
        section_name=req.section_name,
        updated_content=updated_content.strip()
    )