"""
DocForge AI — document_utils.py
  1. markdown_to_plain_text()     — strip all markdown → clean plain text
  2. get_words_per_section()      — industry-standard lengths per doc type
  3. build_plain_text_document()  — assemble full plain-text doc string
"""
import re
from typing import Dict, List, Optional


# ─── Markdown → Plain Text ────────────────────────────────────────────────────

def markdown_to_plain_text(md: str) -> str:
    """Strip all markdown syntax and return clean plain text."""
    t = md
    t = re.sub(r'^---+\s*$', '', t, flags=re.MULTILINE)         # hr
    t = re.sub(r'^\*\*\*+\s*$', '', t, flags=re.MULTILINE)      # hr variant
    t = re.sub(r'<[^>]+>', '', t)                                 # html tags
    t = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', t)              # links
    t = re.sub(r'`{3}.*?`{3}', '', t, flags=re.DOTALL)          # code blocks
    t = re.sub(r'`([^`]+)`', r'\1', t)                           # inline code
    t = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', t)                  # bold+italic
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)                      # bold
    t = re.sub(r'\*(.+?)\*', r'\1', t)                          # italic
    t = re.sub(r'__(.+?)__', r'\1', t)                          # bold alt
    t = re.sub(r'_(.+?)_', r'\1', t)                            # italic alt
    t = re.sub(r'^#{1,6}\s+', '', t, flags=re.MULTILINE)        # headings
    t = re.sub(r'^\s*[-*+]\s+', '  - ', t, flags=re.MULTILINE) # bullets → plain
    t = re.sub(r'^\s*(\d+)\.\s+', r'\1. ', t, flags=re.MULTILINE)  # numbered
    t = re.sub(r'\|', ' ', t)                                    # table pipes
    t = re.sub(r'^[\s\-:=]+$', '', t, flags=re.MULTILINE)       # table dividers
    t = re.sub(r'\n{3,}', '\n\n', t)                             # excess blanks
    lines = [line.rstrip() for line in t.split('\n')]
    return '\n'.join(lines).strip()


# ─── Industry-Standard Length Map ────────────────────────────────────────────
# Total target word count per document type

DOC_WORD_TARGETS: Dict[str, int] = {
    # HR
    "Employee Offer Letter": 350,
    "Employment Contract": 700,
    "Employee Handbook": 1800,
    "Performance Review Report": 500,
    "Leave Approval Letter": 200,
    "Disciplinary Notice": 350,
    "Internship Agreement": 500,
    "Exit Clearance Form": 250,
    "Job Description Document": 450,
    "Training Completion Certificate": 180,
    # Finance
    "Invoice": 200,
    "Purchase Order": 220,
    "Expense Reimbursement Form": 200,
    "Budget Report": 600,
    "Payment Receipt": 160,
    "Vendor Payment Approval": 250,
    "Financial Statement Summary": 550,
    "Tax Filing Summary": 450,
    "Cost Analysis Report": 600,
    "Refund Authorization Form": 200,
    # Legal
    "Non-Disclosure Agreement (NDA)": 900,
    "Service Agreement": 1000,
    "Partnership Agreement": 1200,
    "Terms of Service": 1500,
    "Privacy Policy": 1400,
    "Vendor Contract": 1000,
    "Licensing Agreement": 900,
    "Legal Notice Letter": 350,
    "Compliance Certification": 400,
    "Intellectual Property Assignment": 700,
    # Sales
    "Sales Proposal": 700,
    "Sales Contract": 800,
    "Quotation Document": 250,
    "Sales Agreement": 600,
    "Deal Summary Report": 450,
    "Commission Report": 350,
    "Customer Onboarding Document": 550,
    "Discount Approval Form": 200,
    "Lead Qualification Report": 350,
    "Renewal Agreement": 550,
    # Marketing
    "Marketing Campaign Plan": 800,
    "Content Strategy Document": 700,
    "Social Media Plan": 600,
    "Brand Guidelines": 1000,
    "Market Research Report": 900,
    "Press Release": 450,
    "SEO Strategy Report": 700,
    "Advertising Brief": 450,
    "Email Campaign Plan": 550,
    "Influencer Agreement": 600,
    # IT
    "IT Access Request Form": 250,
    "Incident Report": 450,
    "System Maintenance Report": 350,
    "Software Installation Request": 200,
    "Data Backup Policy": 600,
    "Security Incident Report": 500,
    "IT Asset Allocation Form": 200,
    "Network Access Agreement": 450,
    "Software License Report": 350,
    "System Upgrade Proposal": 550,
    # Operations
    "Standard Operating Procedure (SOP)": 900,
    "Operations Report": 550,
    "Process Improvement Plan": 600,
    "Risk Assessment Report": 600,
    "Inventory Report": 350,
    "Production Plan": 550,
    "Logistics Plan": 550,
    "Supplier Evaluation Report": 450,
    "Quality Control Checklist": 350,
    "Business Continuity Plan": 800,
    # Customer Support
    "Support Ticket Report": 350,
    "Customer Complaint Report": 450,
    "Customer Feedback Report": 500,
    "SLA Agreement": 700,
    "Support Resolution Report": 350,
    "Customer Escalation Report": 350,
    "Service Improvement Plan": 550,
    "Customer Onboarding Guide": 600,
    "FAQ Document": 550,
    "Support Training Manual": 800,
    # Procurement
    "Vendor Registration Form": 350,
    "Vendor Evaluation Report": 450,
    "Purchase Requisition": 200,
    "Vendor Contract": 900,
    "Procurement Plan": 600,
    "Bid Evaluation Report": 550,
    "Supplier Risk Assessment": 550,
    "Contract Renewal Notice": 250,
    "Delivery Acceptance Report": 250,
    "Procurement Compliance Checklist": 300,
    # Product Management
    "Product Requirements Document (PRD)": 1000,
    "Product Roadmap": 600,
    "Feature Specification": 550,
    "Release Notes": 350,
    "Product Launch Plan": 700,
    "Competitive Analysis Report": 600,
    "Product Strategy Document": 800,
    "User Persona Document": 450,
    "Product Feedback Report": 450,
    "Product Change Request": 350,
}

DEFAULT_TOTAL_WORDS = 500


def get_words_per_section(doc_type: str, num_sections: int) -> int:
    """Return target words per section, clamped to [60, 300]."""
    total = DOC_WORD_TARGETS.get(doc_type, DEFAULT_TOTAL_WORDS)
    n = max(num_sections, 1)
    per_sec = total // n
    return max(60, min(300, per_sec))


# ─── Plain Text Document Assembler ───────────────────────────────────────────

def build_plain_text_document(
    doc_type: str,
    department: str,
    company_name: str,
    industry: str,
    region: str,
    active_sections: List[str],
    section_contents: Dict[str, str],
) -> str:
    """
    Assemble a clean plain-text document from section contents.
    No markdown, no asterisks, no # symbols — pure text for storage/export.
    """
    lines = [
        doc_type.upper(),
        "=" * len(doc_type),
        "",
        f"Organization:       {company_name}",
        f"Department:         {department}",
        f"Industry:           {industry}",
        f"Region:             {region}",
        f"Document Version:   v1.0",
        f"Classification:     Internal Use Only",
        f"Generated by:       DocForge AI",
        "",
        "-" * 60,
        "",
    ]

    for sec_name in active_sections:
        content = section_contents.get(sec_name, "").strip()
        if not content:
            continue
        clean = markdown_to_plain_text(content)
        lines.append(sec_name.upper())
        lines.append("-" * len(sec_name))
        lines.append("")
        lines.append(clean)
        lines.append("")
        lines.append("")

    return "\n".join(lines).strip()
