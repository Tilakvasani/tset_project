from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class Industry(str, Enum):
    SAAS = "SaaS"

class Department(str, Enum):
    HR = "Human Resources (HR)"
    LEGAL = "Legal"
    FINANCE = "Finance / Accounting"
    SALES = "Sales"
    MARKETING = "Marketing"
    ENGINEERING = "Engineering / Development"
    PRODUCT = "Product Management"
    OPERATIONS = "Operations"
    CUSTOMER_SUPPORT = "Customer Support"
    COMPLIANCE = "Compliance / Risk Management"

class DocType(str, Enum):
    TERMS_OF_SERVICE = "Terms of Service"
    EMPLOYMENT_CONTRACT = "Employment Contract"
    PRIVACY_POLICY = "Privacy Policy"
    SOP = "SOP"
    SLA = "SLA"
    PRD = "Product Requirement Document"
    TECHNICAL_SPECIFICATION = "Technical Specification"
    INCIDENT_REPORT = "Incident Report"
    SECURITY_POLICY = "Security Policy"
    CUSTOMER_ONBOARDING = "Customer Onboarding Guide"
    BUSINESS_PROPOSAL = "Business Proposal"
    NDA = "NDA"

class SectionAnswers(BaseModel):
    """The 14 answers collected across the 7 guided sections"""
    # Section 1 — Title & Overview
    doc_title: Optional[str] = ""
    doc_version: Optional[str] = ""
    # Section 2 — Purpose
    purpose_main: Optional[str] = ""
    purpose_problem: Optional[str] = ""
    # Section 3 — Scope
    scope_applies: Optional[str] = ""
    scope_exclusions: Optional[str] = ""
    # Section 4 — Responsibilities
    resp_implement: Optional[str] = ""
    resp_maintain: Optional[str] = ""
    # Section 5 — Procedure / Process
    proc_steps: Optional[str] = ""
    proc_tools: Optional[str] = ""
    # Section 6 — Compliance & Risk
    comp_regs: Optional[str] = ""
    comp_risks: Optional[str] = ""
    # Section 7 — Conclusion
    conc_outcome: Optional[str] = ""
    conc_review: Optional[str] = ""


class DocumentRequest(BaseModel):
    title: str = Field(..., description="Document title")
    industry: Industry = Field(default=Industry.SAAS, description="Target industry")
    department: Optional[str] = Field(None, description="Department e.g. Legal, HR")
    doc_type: DocType = Field(..., description="Type of document")
    description: Optional[str] = Field(None, description="Compiled section answers as description")
    tags: Optional[List[str]] = Field(default=[], description="Tags for the document")
    created_by: Optional[str] = Field(default="admin", description="Creator name")
    section_answers: Optional[SectionAnswers] = Field(None, description="All 7 section Q&A answers")


class DocumentResponse(BaseModel):
    doc_id: str
    title: str
    industry: str
    department: Optional[str] = None
    doc_type: str
    content: str
    tags: List[str]
    created_by: str
    created_at: datetime
    version: str = "v1.0"
    notion_url: Optional[str] = None
    published: bool = False
    section_answers: Optional[SectionAnswers] = None