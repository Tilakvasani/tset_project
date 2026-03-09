from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class Industry(str, Enum):
    SAAS = "SaaS"

class DocType(str, Enum):
    NDA = "NDA"
    SOP="SOP"
    PRIVACY_POLICY = "Privacy Policy"
    TERMS_OF_SERVICE = "Terms of Service"
    EMPLOYMENT_CONTRACT = "Employment Contract"
    SLA = "SLA"
    BUSINESS_PROPOSAL = "Business Proposal"
    TECHNICAL_SPEC = "Technical Spec"
    PROJECT_CHARTER = "Project Charter"
    RISK_ASSESSMENT = "Risk Assessment"
    COMPLIANCE_REPORT = "Compliance Report"
    INVOICE_TEMPLATE = "Invoice Template"
    PARTNERSHIP_AGREEMENT = "Partnership Agreement"

class DocumentRequest(BaseModel):
    title: str = Field(..., description="Document title")
    industry: Industry = Field(default=Industry.SAAS, description="Target industry")
    doc_type: DocType = Field(..., description="Type of document")
    description: Optional[str] = Field(None, description="Brief context or description")
    tags: Optional[List[str]] = Field(default=[], description="Tags for the document")
    created_by: Optional[str] = Field(default="admin", description="Creator name")

class DocumentResponse(BaseModel):
    doc_id: str
    title: str
    industry: str
    doc_type: str
    content: str
    tags: List[str]
    created_by: str
    created_at: datetime
    version: str = "v1.0"
    notion_url: Optional[str] = None
    published: bool = False