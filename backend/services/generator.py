from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.core.config import settings
from backend.core.logger import logger
from backend.schemas.document_schema import DocumentRequest, DocumentResponse
from backend.models.document_model import DocumentModel
from prompts.templates import get_prompt_template
from prompts.quality_gates import check_quality
from datetime import datetime
import uuid

def get_model(temperature: float = 0.7):
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        api_key=settings.GROQ_API_KEY
    )

def get_value(field) -> str:
    """Safely extract string value from either enum or plain string"""
    if hasattr(field, 'value'):
        return field.value
    return str(field)

async def generate_document(request: DocumentRequest) -> DocumentResponse:
    """Generate a document using LangChain + Groq"""
    industry_val = get_value(request.industry)
    doc_type_val = get_value(request.doc_type)

    logger.info(f"Starting generation: {doc_type_val} | {industry_val}")

    template_str = get_prompt_template(request.doc_type)

    prompt = PromptTemplate(
        template=template_str,
        input_variables=["title", "industry", "description"]
    )

    parser = StrOutputParser()
    model = get_model()
    chain = prompt | model | parser

    description = request.description or f"A professional {doc_type_val} document for the {industry_val} industry"

    content = chain.invoke({
        "title": request.title,
        "industry": industry_val,
        "description": description
    })

    # Quality gate check
    passed, reason = check_quality(content, request.doc_type)
    if not passed:
        logger.warning(f"Quality gate failed: {reason}. Regenerating...")
        content = chain.invoke({
            "title": request.title,
            "industry": industry_val,
            "description": f"{description}. Make sure to include all required sections."
        })

    tags = request.tags or [industry_val, doc_type_val]

    doc = DocumentModel(
        doc_id=str(uuid.uuid4()),
        title=request.title,
        industry=industry_val,
        doc_type=doc_type_val,
        content=content,
        tags=tags,
        created_by=request.created_by or "admin",
        created_at=datetime.utcnow(),
    )

    logger.info(f"Document generated successfully: {doc.doc_id}")

    return DocumentResponse(
        doc_id=doc.doc_id,
        title=doc.title,
        industry=doc.industry,
        doc_type=doc.doc_type,
        content=doc.content,
        tags=doc.tags,
        created_by=doc.created_by,
        created_at=doc.created_at,
        version=doc.version,
        published=False
    )