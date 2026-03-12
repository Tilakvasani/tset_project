from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── Step 1: Load Departments & Doc Types ────────────────────────────────────

class DepartmentResponse(BaseModel):
    doc_id: int
    department: str
    doc_types: List[str]


# ─── Step 2: Load Sections for a Doc Type ────────────────────────────────────

class SectionResponse(BaseModel):
    doc_sec_id: int
    doc_type: str
    doc_sec: List[str]


# ─── Step 3: Generate Questions (LLM) ────────────────────────────────────────

class GenerateQuestionsRequest(BaseModel):
    doc_sec_id: int                         # FK → document_section
    doc_id: int                             # FK → depart
    section_name: str                       # e.g. "Job Position Details"
    doc_type: str                           # e.g. "Employee Offer Letter"
    department: str                         # e.g. "HR"
    company_context: Optional[Dict[str, str]] = Field(
        default={},
        description="Company name, industry, size, region"
    )

class GenerateQuestionsResponse(BaseModel):
    sec_id: int                             # PK from section_que_ans
    doc_sec_id: int
    doc_id: int
    section_name: str
    questions: List[str]                    # LLM-generated questions


# ─── Step 4: Save User Answers ────────────────────────────────────────────────

class SaveAnswersRequest(BaseModel):
    sec_id: int                             # FK → section_que_ans
    doc_sec_id: int
    doc_id: int
    section_name: str
    questions: List[str]
    answers: List[str]


class SaveAnswersResponse(BaseModel):
    sec_id: int
    section_name: str
    saved: bool


# ─── Step 5: Generate Section Content (LLM) ──────────────────────────────────

class GenerateSectionRequest(BaseModel):
    sec_id: int                             # FK → section_que_ans
    doc_sec_id: int
    doc_id: int
    section_name: str
    doc_type: str
    department: str
    company_context: Optional[Dict[str, str]] = {}


class GenerateSectionResponse(BaseModel):
    sec_id: int
    section_name: str
    content: str                            # Generated markdown prose


# ─── Step 6: Combine Sections → Full Document ────────────────────────────────

class CombineDocumentRequest(BaseModel):
    doc_id: int
    doc_sec_id: int
    doc_type: str
    department: str
    sec_ids: List[int]                      # All section sec_ids in order
    company_context: Optional[Dict[str, str]] = {}


class CombineDocumentResponse(BaseModel):
    gen_id: int                             # PK from gen_doc
    doc_id: int
    doc_sec_id: int
    doc_type: str
    department: str
    gen_doc_sec_dec: List[str]              # Section content list
    gen_doc_full: str                       # Full assembled document


# ─── Step 7: Edit / Enhance a Section ────────────────────────────────────────

class EditSectionRequest(BaseModel):
    gen_id: int                             # FK → gen_doc
    sec_id: int
    section_name: str
    current_content: str
    edit_instruction: str                   # e.g. "Make it more formal"


class EditSectionResponse(BaseModel):
    sec_id: int
    section_name: str
    updated_content: str


# ─── Step 8: Publish to Notion ───────────────────────────────────────────────

class NotionPublishRequest(BaseModel):
    gen_id: int
    doc_type: str
    department: str
    gen_doc_full: str
    company_context: Optional[Dict[str, str]] = {}


class NotionPublishResponse(BaseModel):
    notion_url: str
    notion_page_id: str


# ─── Step 9: Download ────────────────────────────────────────────────────────

class DownloadRequest(BaseModel):
    gen_id: int
    format: str = Field(..., description="pdf or docx")
    gen_doc_full: str
    doc_type: str