"""
DocForge AI — prompts/templates.py
════════════════════════════════════════════════════════════════
Source of truth: https://www.notion.so/all-doc-section-31f12206f265809885e1d52cc5a6897b
100 document types · 7 departments · exact sections per doc
"""

# ─────────────────────────────────────────────────────────────────────────────
#  DEPARTMENT → DOCUMENT TYPES  (exact from Notion page)
# ─────────────────────────────────────────────────────────────────────────────
DOC_TYPES_BY_CATEGORY = {
    "HR": [
        "Employee Offer Letter",
        "Employment Contract",
        "Employee Handbook",
        "Performance Review Report",
        "Leave Approval Letter",
        "Disciplinary Notice",
        "Internship Agreement",
        "Exit Clearance Form",
        "Job Description Document",
        "Training Completion Certificate",
    ],
    "Finance": [
        "Invoice",
        "Purchase Order",
        "Expense Reimbursement Form",
        "Budget Report",
        "Payment Receipt",
        "Vendor Payment Approval",
        "Financial Statement Summary",
        "Tax Filing Summary",
        "Cost Analysis Report",
        "Refund Authorization Form",
    ],
    "Legal": [
        "Non-Disclosure Agreement (NDA)",
        "Service Agreement",
        "Partnership Agreement",
        "Terms of Service",
        "Privacy Policy",
        "Vendor Contract",
        "Licensing Agreement",
        "Legal Notice Letter",
        "Compliance Certification",
        "Intellectual Property Assignment",
    ],
    "Sales": [
        "Sales Proposal",
        "Sales Contract",
        "Quotation Document",
        "Sales Agreement",
        "Deal Summary Report",
        "Commission Report",
        "Customer Onboarding Document",
        "Discount Approval Form",
        "Lead Qualification Report",
        "Renewal Agreement",
    ],
    "Marketing": [
        "Marketing Campaign Plan",
        "Content Strategy Document",
        "Social Media Plan",
        "Brand Guidelines",
        "Market Research Report",
        "Press Release",
        "SEO Strategy Report",
        "Advertising Brief",
        "Email Campaign Plan",
        "Influencer Agreement",
    ],
    "IT": [
        "IT Access Request Form",
        "Incident Report",
        "System Maintenance Report",
        "Software Installation Request",
        "Data Backup Policy",
        "Security Incident Report",
        "IT Asset Allocation Form",
        "Network Access Agreement",
        "Software License Report",
        "System Upgrade Proposal",
    ],
    "Operations": [
        "Standard Operating Procedure (SOP)",
        "Operations Report",
        "Process Improvement Plan",
        "Risk Assessment Report",
        "Inventory Report",
        "Production Plan",
        "Logistics Plan",
        "Supplier Evaluation Report",
        "Quality Control Checklist",
        "Business Continuity Plan",
    ],
    "Customer Support": [
        "Support Ticket Report",
        "Customer Complaint Report",
        "Customer Feedback Report",
        "SLA Agreement",
        "Support Resolution Report",
        "Customer Escalation Report",
        "Service Improvement Plan",
        "Customer Onboarding Guide",
        "FAQ Document",
        "Support Training Manual",
    ],
    "Procurement": [
        "Vendor Registration Form",
        "Vendor Evaluation Report",
        "Purchase Requisition",
        "Vendor Contract",
        "Procurement Plan",
        "Bid Evaluation Report",
        "Supplier Risk Assessment",
        "Contract Renewal Notice",
        "Delivery Acceptance Report",
        "Procurement Compliance Checklist",
    ],
    "Product Management": [
        "Product Requirements Document (PRD)",
        "Product Roadmap",
        "Feature Specification",
        "Release Notes",
        "Product Launch Plan",
        "Competitive Analysis Report",
        "Product Strategy Document",
        "User Persona Document",
        "Product Feedback Report",
        "Product Change Request",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
#  PROMPT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def build_answers_block(answers: dict, sections: list) -> str:
    lines = []
    for sec in sections:
        lines.append(f"\n[{sec['name']}]")
        for (key, label, _) in sec.get("questions", []):
            val = answers.get(key, "Not provided")
            lines.append(f"  Q: {label}")
            lines.append(f"  A: {val}")
    return "\n".join(lines)


PHASE_2_PROMPT = """You are an enterprise documentation specialist.

DOCUMENT TYPE: {doc_type}
INDUSTRY: {industry}
DEPARTMENT: {department}

USER ANSWERS BY SECTION:
{answers_block}

Generate a complete, professional enterprise document. Requirements:
1. Start with ## [Section Name] for each section header.
2. Expand user answers into professional prose — do not copy answers verbatim.
3. 150–300 words per section.
4. Maintain consistent terminology throughout.
5. Use markdown tables for RACI, comparison data, or structured lists.
6. End with an Approvals and Sign-off section with a signature table.
7. Professional enterprise tone throughout.

Generate the complete document now:"""