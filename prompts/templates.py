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

DEPARTMENTS  = list(DOC_TYPES_BY_CATEGORY.keys())
ALL_DOC_TYPES = [doc for docs in DOC_TYPES_BY_CATEGORY.values() for doc in docs]


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION DEFINITIONS
#  Each section: {"name": str, "icon": str, "freq": str, "questions": [(key, label, placeholder), ...]}
# ─────────────────────────────────────────────────────────────────────────────

_SECTIONS: dict[str, list[dict]] = {

    # ── HR ────────────────────────────────────────────────────────────────────

    "Employee Offer Letter": [
        {"name": "Job Position Details",       "icon": "💼", "freq": "100%", "questions": [("job_title", "Job title and department", "e.g. Senior Software Engineer, Engineering"), ("reporting_manager", "Reporting manager name and title", "e.g. Aisha Patel, VP Engineering")]},
        {"name": "Employment Start Date",      "icon": "📅", "freq": "100%", "questions": [("start_date", "Proposed joining date", "e.g. April 1, 2026"), ("start_conditions", "Any conditions before start", "e.g. Background check, reference verification")]},
        {"name": "Compensation and Salary",    "icon": "💰", "freq": "100%", "questions": [("salary", "Offered salary and components", "e.g. $95,000 base + $10,000 annual bonus"), ("pay_frequency", "Payment frequency", "e.g. Monthly, bi-weekly")]},
        {"name": "Employee Benefits",          "icon": "🎁", "freq": "98%",  "questions": [("benefits", "List of benefits offered", "e.g. Health insurance, 20 days PTO, 401k matching"), ("perks", "Additional perks", "e.g. Remote work, gym allowance")]},
        {"name": "Employment Type",            "icon": "📋", "freq": "100%", "questions": [("emp_type", "Employment type", "e.g. Full-time permanent"), ("work_location", "Primary work location", "e.g. New York HQ / Remote")]},
        {"name": "Probation Period",           "icon": "⏳", "freq": "88%",  "questions": [("probation_duration", "Probation duration", "e.g. 3 months"), ("probation_criteria", "Evaluation criteria during probation", "e.g. Quarterly OKR review, manager assessment")]},
        {"name": "Acceptance Instructions",    "icon": "✅", "freq": "100%", "questions": [("acceptance_deadline", "Offer acceptance deadline", "e.g. March 25, 2026"), ("acceptance_method", "How to accept", "e.g. Sign and return by email to hr@company.com")]},
    ],

    "Employment Contract": [
        {"name": "Position and Job Responsibilities", "icon": "💼", "freq": "100%", "questions": [("job_title", "Job title and department", "e.g. Product Manager, Product Management"), ("duties", "Primary duties and responsibilities", "e.g. Lead product roadmap, manage cross-functional teams")]},
        {"name": "Employment Duration",               "icon": "📅", "freq": "100%", "questions": [("start_date", "Employment start date", "e.g. April 1, 2026"), ("contract_type", "Contract type", "e.g. Permanent / Fixed-term 12 months")]},
        {"name": "Work Schedule",                     "icon": "🕐", "freq": "95%",  "questions": [("work_hours", "Working hours and days", "e.g. 40 hours/week, Mon–Fri 9am–6pm"), ("flexibility", "Any flexibility or shift arrangements", "e.g. Flexible start time, hybrid 3 days in office")]},
        {"name": "Compensation and Salary Terms",     "icon": "💰", "freq": "100%", "questions": [("salary", "Salary and payment schedule", "e.g. $110,000 per year paid monthly"), ("bonuses", "Bonuses, incentives, allowances", "e.g. 15% annual performance bonus, travel allowance")]},
        {"name": "Confidentiality and Non-Disclosure","icon": "🔒", "freq": "96%",  "questions": [("confidential_scope", "Scope of confidential information", "e.g. All business strategies, client data, source code"), ("nda_duration", "Duration of confidentiality obligations", "e.g. Survives termination for 2 years")]},
        {"name": "Termination and Notice Period",     "icon": "📤", "freq": "100%", "questions": [("notice_period", "Notice period required by either party", "e.g. 30 days written notice"), ("termination_grounds", "Grounds for immediate termination", "e.g. Gross misconduct, breach of policy")]},
        {"name": "Governing Law",                     "icon": "⚖️", "freq": "100%", "questions": [("jurisdiction", "Legal jurisdiction", "e.g. State of California, USA"), ("dispute_resolution", "Dispute resolution method", "e.g. Binding arbitration under AAA rules")]},
    ],

    "Employee Handbook": [
        {"name": "About the Company",              "icon": "🏢", "freq": "100%", "questions": [("mission", "Company mission and vision", "e.g. To democratize enterprise software for SMBs"), ("culture", "Company values and culture", "e.g. Transparency, ownership, customer obsession")]},
        {"name": "Employment Policies",            "icon": "📋", "freq": "100%", "questions": [("eeo_policy", "Equal opportunity and non-discrimination policy", "e.g. We do not discriminate on race, gender, age, religion"), ("ethics", "Workplace ethics expectations", "e.g. Integrity, respect, conflict of interest disclosure")]},
        {"name": "Working Hours and Attendance",   "icon": "🕐", "freq": "100%", "questions": [("work_schedule", "Work schedule and attendance requirements", "e.g. Core hours 10am–4pm, 40hr/week"), ("absence_procedure", "How to report absences", "e.g. Notify manager before 9am via Slack or call")]},
        {"name": "Leave and Time-Off Policies",    "icon": "🌴", "freq": "100%", "questions": [("leave_types", "Types of leave available", "e.g. 20 days annual, 10 days sick, 16 weeks parental"), ("leave_request", "Process for requesting leave", "e.g. Submit request in HR system 2 weeks in advance")]},
        {"name": "IT and Acceptable Use",          "icon": "💻", "freq": "95%",  "questions": [("it_policy", "Rules for company technology use", "e.g. No personal use of company devices, no unapproved software"), ("data_protection", "Data protection responsibilities", "e.g. Do not share passwords, use VPN on public wifi")]},
        {"name": "Disciplinary Procedures",        "icon": "⚠️", "freq": "98%",  "questions": [("disciplinary_steps", "Steps in disciplinary process", "e.g. Verbal warning → written warning → suspension → termination"), ("violations", "Examples of policy violations", "e.g. Harassment, data breach, repeated lateness")]},
        {"name": "Employee Grievance Procedure",   "icon": "🗣️", "freq": "92%",  "questions": [("grievance_process", "How employees raise concerns", "e.g. Report to direct manager or HR; anonymous hotline available"), ("escalation", "Escalation path if unresolved", "e.g. HR Director → CEO within 14 days")]},
    ],

    "Performance Review Report": [
        {"name": "Employee Information",           "icon": "👤", "freq": "100%", "questions": [("employee_name", "Employee name, title, department", "e.g. James Chen, Senior Developer, Engineering"), ("review_period", "Review period dates", "e.g. January 1 – December 31, 2025")]},
        {"name": "Performance Objectives and Goals","icon":"🎯", "freq": "100%", "questions": [("goals", "Goals set at the start of review period", "e.g. Launch 3 features, reduce bug backlog by 40%"), ("goal_completion", "Completion status of each goal", "e.g. Feature launch: complete; Bug reduction: 35% achieved")]},
        {"name": "Key Achievements",               "icon": "🏆", "freq": "100%", "questions": [("achievements", "Major accomplishments this period", "e.g. Led migration to microservices, mentored 2 junior devs"), ("impact", "Business impact of achievements", "e.g. Reduced deployment time by 60%, improved team velocity")]},
        {"name": "Performance Metrics and Ratings","icon": "📊", "freq": "100%", "questions": [("metrics", "Key metrics and scores", "e.g. Code quality: 4/5, Teamwork: 5/5, Delivery: 3/5"), ("overall_rating", "Overall performance rating", "e.g. Meets Expectations / Exceeds / Below")]},
        {"name": "Areas for Improvement",          "icon": "📈", "freq": "100%", "questions": [("improvement_areas", "Areas needing development", "e.g. Communication with stakeholders, estimation accuracy"), ("support_offered", "Support or resources offered", "e.g. Communication training, PM shadowing program")]},
        {"name": "Development Plan",               "icon": "🗺️", "freq": "95%",  "questions": [("dev_goals", "Development goals for next period", "e.g. Complete AWS certification, lead a project end-to-end"), ("training", "Recommended training or development activities", "e.g. Leadership workshop Q2, external conference")]},
        {"name": "Performance Outcome",            "icon": "✅", "freq": "100%", "questions": [("outcome", "Result of review", "e.g. Promotion to Lead, salary increase of 8%"), ("next_review", "Date of next review", "e.g. June 30, 2026")]},
    ],

    "Leave Approval Letter": [
        {"name": "Leave Details",           "icon": "🌴", "freq": "100%", "questions": [("leave_type", "Type of leave approved", "e.g. Annual leave / Sick leave / Maternity leave"), ("leave_dates", "Approved start and end dates", "e.g. April 14 – April 25, 2026")]},
        {"name": "Work Handover",           "icon": "🔄", "freq": "88%",  "questions": [("handover_person", "Who will cover responsibilities", "e.g. Priya Sharma will handle all urgent matters"), ("handover_tasks", "Key tasks to be handed over", "e.g. Weekly standup, client calls, incident response")]},
        {"name": "Return to Work",          "icon": "📅", "freq": "100%", "questions": [("return_date", "Expected return to work date", "e.g. April 28, 2026"), ("return_conditions", "Any conditions upon return", "e.g. Submit medical certificate if sick leave exceeds 3 days")]},
        {"name": "Conditions or Notes",     "icon": "📝", "freq": "85%",  "questions": [("conditions", "Special conditions or policy notes", "e.g. Leave counted against annual entitlement"), ("additional_notes", "Additional remarks", "e.g. Emergency contact available at +1-555-0199")]},
    ],

    "Disciplinary Notice": [
        {"name": "Description of the Incident",   "icon": "📋", "freq": "100%", "questions": [("incident_date", "Date and description of incident", "e.g. March 5, 2026 — arrived 2 hours late without notice"), ("circumstances", "Circumstances surrounding the incident", "e.g. Third occurrence in 60 days; prior warnings given")]},
        {"name": "Policy Violation",              "icon": "⚠️", "freq": "100%", "questions": [("policy_violated", "Specific policy or rule violated", "e.g. Attendance Policy section 3.2 — punctuality requirement"), ("severity", "Severity level of violation", "e.g. Minor / Moderate / Serious")]},
        {"name": "Corrective Actions Required",   "icon": "🔧", "freq": "100%", "questions": [("corrective_actions", "Actions employee must take", "e.g. Arrive on time for 90 days, submit daily attendance log"), ("deadline", "Deadline for corrective action", "e.g. Must demonstrate improvement within 30 days")]},
        {"name": "Consequences of Further Violations","icon":"🚨","freq":"100%","questions":[("consequences", "Consequences if behavior continues", "e.g. Suspension without pay, potential termination"), ("appeal_process", "Employee's right to appeal", "e.g. May submit written appeal to HR within 5 business days")]},
    ],

    "Internship Agreement": [
        {"name": "Internship Position",        "icon": "🎓", "freq": "100%", "questions": [("intern_role", "Internship title and department", "e.g. Software Engineering Intern, Product Team"), ("supervisor", "Supervisor or mentor name and title", "e.g. Dr. Mei Lin, Engineering Manager")]},
        {"name": "Internship Duration",        "icon": "📅", "freq": "100%", "questions": [("start_end", "Start and end dates of internship", "e.g. June 1 – August 31, 2026"), ("working_hours", "Working hours and schedule", "e.g. Mon–Fri, 9am–5pm, 40 hours/week")]},
        {"name": "Roles and Responsibilities", "icon": "📝", "freq": "100%", "questions": [("duties", "Intern's key duties and tasks", "e.g. Develop features, write tests, attend sprint reviews"), ("deliverables", "Expected deliverables or projects", "e.g. Complete assigned sprint tasks, produce technical documentation")]},
        {"name": "Stipend and Compensation",   "icon": "💰", "freq": "90%",  "questions": [("stipend", "Stipend amount or unpaid status", "e.g. $2,500/month stipend, paid bi-weekly"), ("benefits", "Any additional benefits or allowances", "e.g. Lunch allowance, transport reimbursement")]},
        {"name": "Confidentiality and IP",     "icon": "🔒", "freq": "95%",  "questions": [("ip_ownership", "Who owns work produced during internship", "e.g. All work product is property of the company"), ("confidential_data", "Types of confidential info", "e.g. Source code, client lists, business strategy")]},
    ],

    "Exit Clearance Form": [
        {"name": "Employment Exit Details",      "icon": "🚪", "freq": "100%", "questions": [("last_day", "Employee's last working day", "e.g. March 31, 2026"), ("separation_type", "Type of separation", "e.g. Resignation / Termination / Retirement")]},
        {"name": "Company Asset Return",         "icon": "💻", "freq": "100%", "questions": [("assets_list", "List of company assets to return", "e.g. MacBook Pro (S/N: ABC123), ID card, access badge"), ("asset_condition", "Condition of returned assets", "e.g. Laptop returned in good working condition")]},
        {"name": "IT Access Deactivation",       "icon": "🔐", "freq": "100%", "questions": [("systems_to_deactivate", "Systems and accounts to deactivate", "e.g. Google Workspace, GitHub, AWS, Slack"), ("deactivation_date", "Date of access deactivation", "e.g. March 31, 2026 at 5pm")]},
        {"name": "Knowledge Transfer",           "icon": "🔄", "freq": "95%",  "questions": [("handover_completed", "Knowledge transfer tasks completed", "e.g. Documented all ongoing projects in Notion, handed over client contacts"), ("handover_recipient", "Who received the knowledge transfer", "e.g. Sarah Williams, incoming team lead")]},
    ],

    "Job Description Document": [
        {"name": "Job Title and Overview",       "icon": "💼", "freq": "100%", "questions": [("job_title", "Official job title and brief summary", "e.g. Senior Data Analyst — responsible for business intelligence"), ("department_reporting", "Department and reporting structure", "e.g. Data team, reports to Head of Analytics")]},
        {"name": "Key Responsibilities",         "icon": "📋", "freq": "100%", "questions": [("responsibilities", "Major tasks and day-to-day activities", "e.g. Build dashboards, run A/B analyses, present to leadership"), ("kpis", "Key performance indicators for this role", "e.g. Report accuracy, insight adoption rate, delivery timeliness")]},
        {"name": "Required Qualifications",      "icon": "🎓", "freq": "100%", "questions": [("education", "Education and certification requirements", "e.g. BSc in Statistics or related field; SQL certification preferred"), ("experience", "Experience requirements", "e.g. 3+ years in data analytics, experience with BI tools")]},
        {"name": "Required Skills",              "icon": "⚙️", "freq": "100%", "questions": [("technical_skills", "Technical skills required", "e.g. Python, SQL, Tableau, Excel, Google BigQuery"), ("soft_skills", "Soft skills and competencies", "e.g. Communication, critical thinking, stakeholder management")]},
        {"name": "Career Growth",                "icon": "📈", "freq": "85%",  "questions": [("growth_path", "Career progression opportunities", "e.g. Lead Analyst → Analytics Manager → Head of Data"), ("development", "Learning and development opportunities", "e.g. Conference budget, internal mentorship program")]},
    ],

    "Training Completion Certificate": [
        {"name": "Participant and Training Info", "icon": "🎓", "freq": "100%", "questions": [("participant_name", "Name of employee/participant", "e.g. Carlos Mendez"), ("training_title", "Training program or course name", "e.g. Cybersecurity Fundamentals — Level 2")]},
        {"name": "Training Description",          "icon": "📚", "freq": "100%", "questions": [("training_summary", "Brief description of training content", "e.g. Covered phishing, access control, incident response"), ("training_duration", "Duration and dates of training", "e.g. March 10–12, 2026 · 24 hours total")]},
        {"name": "Skills Acquired",               "icon": "⚡", "freq": "100%", "questions": [("skills", "Key skills or competencies gained", "e.g. Threat identification, secure coding, incident escalation"), ("assessment", "How completion was assessed", "e.g. Written exam with 80% pass mark, practical simulation")]},
    ],

    # ── Finance ───────────────────────────────────────────────────────────────

    "Invoice": [
        {"name": "Client and Billing Details", "icon": "🧾", "freq": "100%", "questions": [("client_name", "Client name and billing address", "e.g. Acme Corp, 123 Business St, New York NY 10001"), ("billing_reference", "PO or service agreement reference", "e.g. PO-2026-0042 / Contract #C-789")]},
        {"name": "Description of Services",    "icon": "📋", "freq": "100%", "questions": [("services", "Products or services provided", "e.g. Web development services — March 2026 (80 hours)"), ("unit_pricing", "Quantity and unit price breakdown", "e.g. 80 hrs × $150/hr = $12,000")]},
        {"name": "Taxes and Totals",           "icon": "💰", "freq": "100%", "questions": [("tax_rate", "Applicable tax rate and amount", "e.g. GST 10% = $1,200"), ("total_due", "Total amount due", "e.g. $13,200 USD")]},
        {"name": "Payment Terms",              "icon": "📅", "freq": "100%", "questions": [("due_date", "Payment due date", "e.g. Net 30 — due April 15, 2026"), ("payment_method", "Payment instructions and bank details", "e.g. Bank transfer to: Wells Fargo, Acct #1234567890, Routing #021000089")]},
    ],

    "Purchase Order": [
        {"name": "Vendor and Order Details",   "icon": "🏭", "freq": "100%", "questions": [("vendor_name", "Vendor/supplier name and address", "e.g. Tech Supplies Ltd, 456 Industrial Ave, Austin TX"), ("order_summary", "Brief description of purchase", "e.g. Office hardware for Q2 refresh — 20 laptops")]},
        {"name": "Item Details",               "icon": "📦", "freq": "100%", "questions": [("items", "Items ordered with specs", "e.g. MacBook Pro 14\" M4, 16GB RAM, 512GB SSD × 20"), ("pricing", "Quantities and unit prices", "e.g. 20 × $2,499 = $49,980")]},
        {"name": "Delivery and Payment",       "icon": "🚚", "freq": "100%", "questions": [("delivery_info", "Delivery address and expected date", "e.g. Ship to HQ, 789 Corp Blvd, by April 30, 2026"), ("payment_terms", "Payment terms", "e.g. Net 45 days from delivery confirmation")]},
        {"name": "Terms and Conditions",       "icon": "📋", "freq": "95%",  "questions": [("quality_standards", "Quality or compliance expectations", "e.g. All items must be new, sealed in original packaging"), ("penalties", "Late delivery or defect penalties", "e.g. 2% penalty per week of delay")]},
    ],

    "Expense Reimbursement Form": [
        {"name": "Expense Details",            "icon": "🧾", "freq": "100%", "questions": [("expense_list", "List of expenses with dates and categories", "e.g. Mar 5: Uber $45 (travel); Mar 7: Hotel $220 (accommodation)"), ("business_purpose", "Business purpose of each expense", "e.g. Client meeting in Chicago — sales conference")]},
        {"name": "Total and Documentation",    "icon": "💰", "freq": "100%", "questions": [("total_amount", "Total reimbursement amount requested", "e.g. $485.50 USD"), ("receipts", "Supporting documents attached", "e.g. Receipts for all expenses above $25 attached")]},
        {"name": "Policy Compliance",          "icon": "✅", "freq": "100%", "questions": [("policy_confirmation", "Confirmation that expenses comply with policy", "e.g. All expenses within approved limits per T&E Policy v2.1"), ("exceptions", "Any out-of-policy expenses needing approval", "e.g. Hotel rate exceeded cap by $20 — business necessity")]},
    ],

    "Budget Report": [
        {"name": "Budget Overview",            "icon": "📊", "freq": "100%", "questions": [("reporting_period", "Reporting period and department", "e.g. Q1 2026 — Engineering Department"), ("total_budget", "Total approved budget", "e.g. $500,000 for Q1 2026")]},
        {"name": "Actual vs Planned Spending", "icon": "📈", "freq": "100%", "questions": [("actual_spend", "Actual spending by category", "e.g. Salaries: $320K, Tools: $45K, Events: $15K"), ("variance", "Variance from plan and explanation", "e.g. Tools overspent by $5K due to new security software purchase")]},
        {"name": "Key Findings and Risks",     "icon": "⚠️", "freq": "95%",  "questions": [("findings", "Key financial insights or concerns", "e.g. Hiring slower than planned; may underspend by $30K"), ("risks", "Financial risks or required adjustments", "e.g. Headcount plan needs revision if hiring picks up in Q2")]},
        {"name": "Recommendations",            "icon": "💡", "freq": "90%",  "questions": [("recommendations", "Actions to improve financial management", "e.g. Reallocate $20K from events to tooling budget"), ("next_steps", "Next review or action date", "e.g. Mid-quarter review scheduled for May 15, 2026")]},
    ],

    "Payment Receipt": [
        {"name": "Payment Details",            "icon": "💳", "freq": "100%", "questions": [("payer_name", "Payer name and organization", "e.g. Globex Corp, 321 Commerce St, Chicago IL"), ("payment_amount", "Amount received and currency", "e.g. $13,200 USD")]},
        {"name": "Transaction Reference",      "icon": "🔢", "freq": "100%", "questions": [("invoice_ref", "Invoice or transaction reference number", "e.g. INV-2026-0088"), ("payment_method", "Payment method used", "e.g. Bank wire transfer, confirmation #TXN-9988")]},
        {"name": "Confirmation",               "icon": "✅", "freq": "100%", "questions": [("payment_date", "Date payment was received", "e.g. March 16, 2026"), ("payment_for", "What the payment was for", "e.g. Web development services — Invoice INV-2026-0088")]},
    ],

    "Vendor Payment Approval": [
        {"name": "Vendor and Invoice Details", "icon": "🏭", "freq": "100%", "questions": [("vendor_name", "Vendor name and invoice number(s)", "e.g. CloudHost Inc — INV #4421, INV #4422"), ("payment_amount", "Payment amount and any deductions", "e.g. $8,500 gross — $500 early payment discount = $8,000 net")]},
        {"name": "Budget Verification",        "icon": "✅", "freq": "100%", "questions": [("budget_line", "Budget line and available funds", "e.g. IT Infrastructure budget — $12,000 remaining in Q1"), ("supporting_docs", "Supporting documents attached", "e.g. Invoices, signed contract, delivery confirmation")]},
        {"name": "Approval Chain",             "icon": "🔐", "freq": "100%", "questions": [("manager_approval", "Manager who approved the payment", "e.g. Tom Richards, Finance Manager"), ("finance_notes", "Finance team verification notes", "e.g. Amounts verified against PO-2026-0110; approved for processing")]},
    ],

    "Financial Statement Summary": [
        {"name": "Revenue and Expense Summary","icon": "📊", "freq": "100%", "questions": [("revenue", "Total revenue for the period", "e.g. $2.4M total revenue — $1.8M SaaS, $600K services"), ("expenses", "Major expense categories and totals", "e.g. Salaries: $1.1M, Infrastructure: $200K, Marketing: $150K")]},
        {"name": "Profit/Loss and Assets",     "icon": "💰", "freq": "100%", "questions": [("net_result", "Net profit or loss", "e.g. Net profit: $650,000 (27% margin)"), ("assets_liabilities", "Summary of assets and liabilities", "e.g. Total assets: $3.2M; Total liabilities: $800K")]},
        {"name": "Management Commentary",      "icon": "📝", "freq": "95%",  "questions": [("commentary", "Key insights from finance leadership", "e.g. Strong ARR growth; COGS increasing due to cloud costs"), ("outlook", "Financial outlook or guidance", "e.g. On track for $10M ARR by Q4 2026")]},
    ],

    "Tax Filing Summary": [
        {"name": "Income and Deductions",      "icon": "📋", "freq": "100%", "questions": [("taxable_income", "Total taxable income for the period", "e.g. $1,850,000 gross income for FY2025"), ("deductions", "Tax deductions and credits applied", "e.g. R&D credit: $45,000; Depreciation: $120,000")]},
        {"name": "Tax Calculation",            "icon": "🧮", "freq": "100%", "questions": [("tax_amount", "Total tax calculated and rate", "e.g. Federal: $320,000 at 21% rate"), ("taxes_paid", "Taxes already paid or estimated payments", "e.g. Q1–Q3 estimated payments: $240,000 paid")]},
        {"name": "Compliance Declaration",     "icon": "⚖️", "freq": "100%", "questions": [("compliance_statement", "Declaration of compliance with regulations", "e.g. Filed in accordance with IRC and state regulations"), ("filed_by", "Responsible officer and filing date", "e.g. CFO Jane Doe — filed March 15, 2026")]},
    ],

    "Cost Analysis Report": [
        {"name": "Cost Categories Overview",   "icon": "📊", "freq": "100%", "questions": [("cost_categories", "Main cost categories being analyzed", "e.g. Direct labor, cloud infrastructure, third-party tools, marketing"), ("analysis_period", "Period covered by the analysis", "e.g. FY2025 Q4 — October to December")]},
        {"name": "Direct and Indirect Costs",  "icon": "💰", "freq": "100%", "questions": [("direct_costs", "Direct costs breakdown", "e.g. Engineering salaries: $450K; AWS: $85K"), ("indirect_costs", "Overhead or indirect costs", "e.g. Office rent: $60K; Admin: $40K; Insurance: $25K")]},
        {"name": "Findings and Recommendations","icon":"💡", "freq": "100%", "questions": [("key_findings", "Key cost insights or anomalies", "e.g. Infrastructure costs grew 40% YoY; engineering headcount cost highest"), ("recommendations", "Cost optimization suggestions", "e.g. Migrate to reserved instances; renegotiate SaaS contracts")]},
    ],

    "Refund Authorization Form": [
        {"name": "Customer and Transaction",   "icon": "👤", "freq": "100%", "questions": [("customer_name", "Customer name and contact", "e.g. John Smith, john@example.com"), ("transaction_ref", "Invoice number and purchase date", "e.g. INV-2026-0044 — purchased March 1, 2026")]},
        {"name": "Refund Request Details",     "icon": "🔄", "freq": "100%", "questions": [("refund_reason", "Reason for refund request", "e.g. Service not delivered as described; product defective"), ("refund_amount", "Amount requested for refund", "e.g. $499 full refund")]},
        {"name": "Processing Details",         "icon": "💳", "freq": "100%", "questions": [("refund_method", "Refund method and timeline", "e.g. Credit card refund within 5–7 business days"), ("approval_notes", "Finance approval notes", "e.g. Verified within 30-day refund window; approved by Finance Manager")]},
    ],

    # ── Legal ─────────────────────────────────────────────────────────────────

    "Non-Disclosure Agreement (NDA)": [
        {"name": "Parties and Purpose",        "icon": "🤝", "freq": "100%", "questions": [("parties", "Disclosing and receiving parties", "e.g. Acme Corp (Disclosing) and XYZ Consulting (Receiving)"), ("purpose", "Why confidential information is being shared", "e.g. Evaluating a potential business partnership")]},
        {"name": "Confidential Information",   "icon": "🔒", "freq": "100%", "questions": [("definition", "What is considered confidential", "e.g. Business strategies, financial data, technical specs, client lists"), ("exclusions", "What is NOT confidential", "e.g. Publicly known info, info independently developed")]},
        {"name": "Obligations and Duration",   "icon": "📋", "freq": "100%", "questions": [("obligations", "Receiving party's obligations", "e.g. Do not disclose, use only for stated purpose, protect with same care as own info"), ("duration", "How long confidentiality obligations last", "e.g. 3 years from date of signing")]},
        {"name": "Remedies and Jurisdiction",  "icon": "⚖️", "freq": "100%", "questions": [("remedies", "Remedies for breach", "e.g. Injunctive relief, monetary damages, legal fees"), ("jurisdiction", "Governing law", "e.g. Laws of the State of Delaware, USA")]},
    ],

    "Service Agreement": [
        {"name": "Scope of Services",          "icon": "📋", "freq": "100%", "questions": [("services", "Specific services to be delivered", "e.g. Custom software development, monthly maintenance, technical support"), ("deliverables", "Expected deliverables and milestones", "e.g. MVP in 8 weeks, full product in 16 weeks, monthly bug fix releases")]},
        {"name": "Timeline and Payment",       "icon": "📅", "freq": "100%", "questions": [("timeline", "Service start, end date, and schedule", "e.g. April 1 – September 30, 2026; sprints every 2 weeks"), ("payment", "Service fees and payment schedule", "e.g. $15,000/month; invoiced on the 1st, due Net 15")]},
        {"name": "Responsibilities",           "icon": "⚖️", "freq": "100%", "questions": [("provider_responsibilities", "Service provider's key obligations", "e.g. Provide qualified team, meet deadlines, attend weekly standups"), ("client_responsibilities", "Client's key obligations", "e.g. Provide timely feedback, supply access credentials, assign product owner")]},
        {"name": "Termination and Governing Law","icon":"🔚","freq":"100%","questions":[("termination", "Termination conditions and notice", "e.g. Either party may terminate with 30 days written notice"), ("governing_law", "Legal jurisdiction", "e.g. Laws of England and Wales")]},
    ],

    "Partnership Agreement": [
        {"name": "Partners and Purpose",       "icon": "🤝", "freq": "100%", "questions": [("partners", "Names and details of all partners", "e.g. Partner A: Acme Corp (60%); Partner B: Beta LLC (40%)"), ("purpose", "Business purpose and objectives", "e.g. Joint development and marketing of SaaS accounting software")]},
        {"name": "Capital and Ownership",      "icon": "💰", "freq": "100%", "questions": [("contributions", "Financial or asset contributions by each partner", "e.g. Acme: $300K cash; Beta: IP rights valued at $200K"), ("ownership", "Ownership percentages and profit sharing", "e.g. Profits distributed 60/40 per ownership share")]},
        {"name": "Governance and Decisions",   "icon": "🗳️", "freq": "100%", "questions": [("roles", "Partner roles and responsibilities", "e.g. Acme: product and tech; Beta: sales and marketing"), ("decision_making", "How major decisions are made", "e.g. Simple majority for operational; unanimous for strategic decisions")]},
        {"name": "Exit and Termination",       "icon": "🚪", "freq": "100%", "questions": [("exit_clause", "Partner exit or withdrawal procedures", "e.g. 90 days notice; buyout at fair market value"), ("dissolution", "Conditions for dissolving partnership", "e.g. Mutual agreement or failure to meet financial targets for 2 consecutive quarters")]},
    ],

    "Terms of Service": [
        {"name": "Service Description and User Eligibility","icon":"📋","freq":"100%","questions":[("service_description", "Description of the platform and services", "e.g. Cloud-based project management platform for teams of all sizes"), ("eligibility", "User eligibility requirements", "e.g. Must be 18+, valid email required, not prohibited by applicable law")]},
        {"name": "User Responsibilities",      "icon": "👤", "freq": "100%", "questions": [("user_obligations", "Acceptable use and user obligations", "e.g. No illegal use, no reverse engineering, no sharing credentials"), ("prohibited", "Prohibited activities", "e.g. Spamming, hacking, scraping, distributing malware")]},
        {"name": "Payment and Intellectual Property","icon":"💰","freq":"100%","questions":[("payment_terms", "Pricing, billing and subscription terms", "e.g. Monthly or annual billing; no refunds for partial periods"), ("ip_rights", "IP ownership and content rights", "e.g. Platform and its content are owned by the company; user retains rights to their data")]},
        {"name": "Liability and Governing Law","icon":"⚖️","freq":"100%","questions":[("liability", "Limitation of liability clause", "e.g. Company not liable for indirect damages; max liability is fees paid in last 3 months"), ("governing_law", "Jurisdiction and dispute resolution", "e.g. Governed by California law; disputes resolved by arbitration in San Francisco")]},
    ],

    "Privacy Policy": [
        {"name": "Data Collected and Usage",   "icon": "🔍", "freq": "100%", "questions": [("data_types", "Types of personal data collected", "e.g. Name, email, IP address, payment info, usage logs"), ("data_purpose", "How the data is used", "e.g. Service delivery, customer support, product improvement, marketing")]},
        {"name": "Data Sharing and Security",  "icon": "🔒", "freq": "100%", "questions": [("sharing", "When and with whom data is shared", "e.g. Shared with payment processors, analytics vendors; never sold"), ("security", "Data protection measures", "e.g. AES-256 encryption, SOC 2 Type II certified, regular pen tests")]},
        {"name": "User Rights and Cookies",    "icon": "⚖️", "freq": "100%", "questions": [("user_rights", "User rights over their personal data", "e.g. Right to access, correct, delete, export, or opt out"), ("cookies", "Cookies and tracking technologies used", "e.g. Session cookies, Google Analytics, Intercom")]},
        {"name": "Retention and Contact",      "icon": "📅", "freq": "100%", "questions": [("retention", "How long data is retained", "e.g. Account data kept for duration of subscription + 90 days"), ("contact", "Privacy contact details", "e.g. privacy@company.com; DPO: Jane Smith")]},
    ],

    "Vendor Contract": [
        {"name": "Scope of Supply",            "icon": "📦", "freq": "100%", "questions": [("products_services", "Products or services to be supplied", "e.g. Annual software licenses for 500 users — Acme HR Platform"), ("specifications", "Product/service specifications and quality standards", "e.g. 99.9% uptime SLA, ISO 27001 certified, GDPR compliant")]},
        {"name": "Pricing and Delivery",       "icon": "💰", "freq": "100%", "questions": [("pricing", "Pricing and payment terms", "e.g. $50,000/year; invoiced quarterly; Net 30 payment"), ("delivery", "Delivery terms and schedule", "e.g. Software access provisioned within 5 business days of signing")]},
        {"name": "Compliance and Termination", "icon": "⚖️", "freq": "100%", "questions": [("compliance", "Compliance and regulatory requirements", "e.g. Vendor must maintain SOC 2, provide annual audit reports"), ("termination", "Termination conditions", "e.g. 60 days written notice; immediate termination for material breach")]},
    ],

    "Licensing Agreement": [
        {"name": "License Grant and Scope",    "icon": "📜", "freq": "100%", "questions": [("ip_description", "Description of licensed intellectual property", "e.g. Proprietary machine learning algorithm — Patent #US10,987,654"), ("license_scope", "Scope and limitations of the license", "e.g. Non-exclusive, non-transferable license for commercial use in North America")]},
        {"name": "Fees and Ownership",         "icon": "💰", "freq": "100%", "questions": [("license_fees", "License fees and payment terms", "e.g. $25,000 upfront + 5% royalty on gross revenue from licensed product"), ("ip_ownership", "Who retains ownership of the IP", "e.g. Licensor retains all ownership rights; licensee gets right to use only")]},
        {"name": "Term and Termination",       "icon": "📅", "freq": "100%", "questions": [("license_term", "Duration of the license", "e.g. 3-year term, renewable by mutual agreement"), ("termination", "Termination conditions", "e.g. Immediate termination on breach; 30 days notice for convenience")]},
    ],

    "Legal Notice Letter": [
        {"name": "Statement of Legal Concern", "icon": "⚠️", "freq": "100%", "questions": [("legal_issue", "Nature of the legal issue or dispute", "e.g. Breach of contract — failure to deliver software by agreed deadline"), ("relevant_clauses", "Relevant contract clauses or legal provisions", "e.g. Section 4.2 of Software Development Agreement dated Jan 15, 2026")]},
        {"name": "Required Action and Deadline","icon":"📋","freq":"100%","questions":[("required_action", "Actions recipient must take", "e.g. Deliver completed software or provide remediation plan within 14 days"), ("consequences", "Consequences of non-compliance", "e.g. Legal proceedings for damages estimated at $150,000")]},
    ],

    "Compliance Certification": [
        {"name": "Applicable Standards",       "icon": "📋", "freq": "100%", "questions": [("regulations", "Regulations or standards being certified against", "e.g. ISO 27001:2022, SOC 2 Type II, GDPR Article 32"), ("scope", "Scope of compliance certification", "e.g. All cloud infrastructure and customer data processing systems")]},
        {"name": "Compliance Evidence",        "icon": "✅", "freq": "100%", "questions": [("evidence", "Evidence or audits supporting compliance", "e.g. Annual third-party audit by Deloitte; penetration testing quarterly"), ("validity", "Certification validity period", "e.g. Valid April 1, 2026 – March 31, 2027")]},
    ],

    "Intellectual Property Assignment": [
        {"name": "IP Description and Assignment","icon":"💡","freq":"100%","questions":[("ip_description", "Description of intellectual property being assigned", "e.g. Custom CRM software including source code, documentation, and design files"), ("assignment_scope", "Scope of rights being transferred", "e.g. All worldwide rights, title, and interest including future improvements")]},
        {"name": "Consideration and Warranties","icon":"💰","freq":"100%","questions":[("compensation", "Compensation or consideration for the assignment", "e.g. One-time payment of $75,000; no ongoing royalties"), ("warranties", "Assignor's representations and warranties", "e.g. IP is original, no third-party claims, no prior assignments")]},
    ],

    # ── Sales ─────────────────────────────────────────────────────────────────

    "Sales Proposal": [
        {"name": "Client Needs and Problem",   "icon": "🎯", "freq": "100%", "questions": [("client_problem", "Client's business challenge or need", "e.g. Manual HR processes causing 20 hours of admin work per week"), ("client_context", "Client's company background and context", "e.g. Series B SaaS company, 150 employees, rapid growth")]},
        {"name": "Proposed Solution",          "icon": "💡", "freq": "100%", "questions": [("solution", "Your proposed product or service solution", "e.g. Automated HR platform with onboarding, payroll, and compliance modules"), ("scope_of_work", "Scope of work and deliverables", "e.g. Implementation in 4 weeks, data migration, 3 months free support")]},
        {"name": "Pricing and Timeline",       "icon": "💰", "freq": "100%", "questions": [("pricing", "Pricing model and costs", "e.g. $2,500/month for up to 200 users; annual commitment discount 20%"), ("timeline", "Implementation or project timeline", "e.g. Go-live in 4 weeks from contract signing")]},
        {"name": "Value Proposition",          "icon": "⭐", "freq": "100%", "questions": [("value", "Key benefits and ROI for client", "e.g. Save 20 hrs/week admin, reduce onboarding time by 60%, ensure compliance"), ("why_us", "Why choose your company", "e.g. 500+ customers, 98% retention rate, dedicated customer success manager")]},
    ],

    "Sales Contract": [
        {"name": "Products/Services and Pricing","icon":"📋","freq":"100%","questions":[("products", "Description of products or services being sold", "e.g. Enterprise CRM software — 50 user licenses, annual subscription"), ("pricing", "Pricing, payment terms, and schedule", "e.g. $60,000/year; 50% upfront, 50% after 90 days")]},
        {"name": "Delivery and Responsibilities","icon":"🚚","freq":"100%","questions":[("delivery", "Delivery schedule or service commencement", "e.g. Software access within 2 business days; training within 2 weeks"), ("responsibilities", "Obligations of both parties", "e.g. Vendor: uptime SLA, support; Customer: timely payment, designated admin")]},
        {"name": "Warranty and Termination",   "icon": "🔐", "freq": "100%", "questions": [("warranty", "Warranty and support terms", "e.g. 12-month warranty; 99.9% uptime SLA; 24/7 priority support"), ("termination", "Termination conditions", "e.g. Either party with 30 days notice; immediate for non-payment")]},
    ],

    "Quotation Document": [
        {"name": "Products/Services and Pricing","icon":"💰","freq":"100%","questions":[("items", "Products or services being quoted", "e.g. 10 × standing desks, 10 × ergonomic chairs, delivery included"), ("pricing_breakdown", "Quantity and unit price breakdown", "e.g. Desks: 10 × $650 = $6,500; Chairs: 10 × $450 = $4,500")]},
        {"name": "Terms and Validity",         "icon": "📅", "freq": "100%", "questions": [("validity", "Quotation validity period", "e.g. Valid for 30 days from March 16, 2026"), ("payment_delivery", "Payment and delivery terms", "e.g. 50% deposit on order; balance on delivery; ships within 10 business days")]},
    ],

    "Sales Agreement": [
        {"name": "Product/Service and Pricing","icon":"📋","freq":"100%","questions":[("product_details", "Products or services being sold", "e.g. Annual SaaS subscription — Analytics Pro Plan, 25 seats"), ("pricing_terms", "Pricing and payment terms", "e.g. $18,000/year billed annually; auto-renews unless cancelled 30 days prior")]},
        {"name": "Delivery and Support",       "icon": "🚚", "freq": "100%", "questions": [("delivery_terms", "Delivery or service commencement terms", "e.g. Access granted within 24 hours of payment; onboarding call within 3 days"), ("support_warranty", "Support and warranty terms", "e.g. Business hours email support; 99.5% uptime SLA; 30-day money-back guarantee")]},
        {"name": "Cancellation and Law",       "icon": "⚖️", "freq": "100%", "questions": [("cancellation", "Cancellation and termination conditions", "e.g. 30 days written notice required; no refunds for unused period"), ("governing_law", "Governing law and jurisdiction", "e.g. Governed by laws of Ontario, Canada")]},
    ],

    "Deal Summary Report": [
        {"name": "Deal Overview",              "icon": "🤝", "freq": "100%", "questions": [("client_deal", "Client name and deal description", "e.g. Acme Corp — 3-year enterprise license, 500 seats"), ("deal_value", "Total deal value and contract terms", "e.g. $450,000 TCV; $150,000 ARR; 3-year contract")]},
        {"name": "Sales Process and Outcome",  "icon": "📈", "freq": "100%", "questions": [("sales_process", "Summary of sales process and key milestones", "e.g. Initial demo Jan 2, proposal Feb 15, negotiation 3 weeks, closed March 10"), ("success_factors", "Key factors that led to closing the deal", "e.g. ROI calculator showing 300% ROI; exec champion; competitive displacement")]},
        {"name": "Insights and Lessons",       "icon": "💡", "freq": "90%",  "questions": [("lessons", "Lessons learned from this deal", "e.g. Multi-threading was key; single contact point caused early delays"), ("revenue_impact", "Revenue impact and next steps", "e.g. Counts toward Q1 quota; expansion opportunity in 6 months")]},
    ],

    "Commission Report": [
        {"name": "Sales Transactions",         "icon": "💰", "freq": "100%", "questions": [("transactions", "Sales transactions with deal values", "e.g. Deal 1: Acme $50K; Deal 2: Beta $30K; Deal 3: Gamma $20K"), ("reporting_period", "Reporting period", "e.g. Q1 2026 — January 1 to March 31")]},
        {"name": "Commission Calculation",     "icon": "🧮", "freq": "100%", "questions": [("commission_rate", "Commission rate and calculation method", "e.g. 8% on all closed-won deals above $10K; 10% above $50K"), ("total_commission", "Total commission earned and any adjustments", "e.g. Gross: $8,000; Clawback for Deal 2 refund: -$500; Net: $7,500")]},
    ],

    "Customer Onboarding Document": [
        {"name": "Product Overview and Setup", "icon": "🚀", "freq": "100%", "questions": [("product_overview", "Overview of purchased product or service", "e.g. DocForge AI — AI document generation platform for enterprise teams"), ("account_setup", "Account setup and first steps", "e.g. Login at app.docforge.ai, invite team, connect Notion workspace")]},
        {"name": "Training and Support",       "icon": "📚", "freq": "100%", "questions": [("training_resources", "Training materials and resources available", "e.g. Video tutorials at help.docforge.ai, weekly live onboarding webinar Tuesdays 3pm"), ("support_contact", "Support channels and contact info", "e.g. Email: support@docforge.ai; Live chat in-app; Phone: 1-800-DOCFORGE")]},
        {"name": "Next Steps and Milestones",  "icon": "🎯", "freq": "95%",  "questions": [("next_steps", "Key next steps for the customer", "e.g. Generate first document this week, invite team by Day 7, review analytics by Day 30"), ("success_criteria", "Success milestones", "e.g. 10 documents generated in first month; all team members active")]},
    ],

    "Discount Approval Form": [
        {"name": "Discount Request Details",   "icon": "💸", "freq": "100%", "questions": [("customer_product", "Customer name and product/service", "e.g. Acme Corp — Enterprise Plan, 100 seats"), ("discount_requested", "Discount amount and reason", "e.g. 25% discount — competitive deal; customer threatening to go with competitor")]},
        {"name": "Revenue Impact and Approval","icon":"📊","freq":"100%","questions":[("revenue_impact", "Impact on revenue or profit margin", "e.g. Standard price $100K/yr; with discount $75K/yr — margin drops from 70% to 60%"), ("approval_justification", "Justification for approving discount", "e.g. Strategic account; 3-year commitment; high expansion potential")]},
    ],

    "Lead Qualification Report": [
        {"name": "Lead Profile",               "icon": "👤", "freq": "100%", "questions": [("lead_info", "Lead company and contact details", "e.g. TechStart Inc — CTO Marcus Williams, 80-person SaaS company, Series A"), ("lead_source", "How the lead was sourced", "e.g. Inbound via website demo request, Google Ads campaign")]},
        {"name": "Qualification Assessment",   "icon": "🎯", "freq": "100%", "questions": [("bant_assessment", "Budget, Authority, Need, Timeline assessment", "e.g. Budget: $50K available; Auth: CTO is decision maker; Need: clear pain; Timeline: Q2"), ("recommendation", "Sales recommendation and next actions", "e.g. Qualified — schedule product demo; assign to enterprise sales rep")]},
    ],

    "Renewal Agreement": [
        {"name": "Renewal Details",            "icon": "🔄", "freq": "100%", "questions": [("original_contract", "Reference to original agreement", "e.g. Service Agreement dated April 1, 2024 — ref SA-2024-041"), ("renewal_changes", "Updated terms or changes for renewal", "e.g. Price increase 5% to $31,500/year; scope expanded to include 2 new modules")]},
        {"name": "Renewal Period and Terms",   "icon": "📅", "freq": "100%", "questions": [("renewal_duration", "New contract period", "e.g. April 1, 2026 – March 31, 2027 (12-month renewal)"), ("payment_termination", "Payment terms and cancellation", "e.g. Annual invoice due April 1; 60 days cancellation notice required")]},
    ],

    # ── Marketing ─────────────────────────────────────────────────────────────

    "Marketing Campaign Plan": [
        {"name": "Campaign Overview",          "icon": "📢", "freq": "100%", "questions": [("campaign_name", "Campaign name and purpose", "e.g. Q2 Product Launch — DocForge AI v2.0 release awareness campaign"), ("objectives", "Measurable campaign objectives", "e.g. 5,000 signups, 500 demos booked, $500K pipeline generated")]},
        {"name": "Target Audience",            "icon": "🎯", "freq": "100%", "questions": [("audience", "Target customer segments", "e.g. HR Directors and IT Managers at SaaS companies 100–500 employees"), ("key_message", "Core marketing message and value proposition", "e.g. Generate enterprise docs 10x faster with AI — no templates needed")]},
        {"name": "Channels and Content",       "icon": "📱", "freq": "100%", "questions": [("channels", "Marketing channels to be used", "e.g. LinkedIn ads, email nurture, webinar, content marketing, partner co-marketing"), ("content_types", "Types of content to be created", "e.g. 3 blog posts, 2 case studies, 1 webinar, 10 social posts, email sequence")]},
        {"name": "Budget and KPIs",            "icon": "💰", "freq": "100%", "questions": [("budget", "Campaign budget and allocation", "e.g. Total $50,000: LinkedIn $25K, Content $10K, Events $10K, Tools $5K"), ("kpis", "KPIs and measurement approach", "e.g. CPL target <$100; Demo-to-close rate >20%; Email open rate >35%")]},
    ],

    "Content Strategy Document": [
        {"name": "Strategy Overview",          "icon": "📝", "freq": "100%", "questions": [("business_goals", "Business objectives for content", "e.g. Increase organic traffic by 100%; establish thought leadership in HR tech"), ("target_audience", "Target audience personas", "e.g. HR Managers at mid-market companies; IT Directors at SaaS startups")]},
        {"name": "Content Themes and Types",   "icon": "🗂️", "freq": "100%", "questions": [("themes", "Content themes and messaging pillars", "e.g. AI in HR, compliance automation, team productivity, enterprise security"), ("content_types", "Content types and formats planned", "e.g. Long-form blog posts, how-to guides, video tutorials, comparison pages, infographics")]},
        {"name": "Workflow and Metrics",       "icon": "📊", "freq": "100%", "questions": [("workflow", "Content creation and approval workflow", "e.g. Writer → SEO review → Editor → Legal check → Publish; 5-day cycle"), ("metrics", "Content performance metrics", "e.g. Organic sessions, keyword rankings, time on page, content-attributed leads")]},
    ],

    "Social Media Plan": [
        {"name": "Platform Strategy",          "icon": "📱", "freq": "100%", "questions": [("platforms", "Platforms selected and justification", "e.g. LinkedIn (B2B audience), Twitter/X (tech community), YouTube (tutorials)"), ("objectives", "Social media objectives", "e.g. 10K LinkedIn followers in 6 months; 5% engagement rate; 50 leads/month")]},
        {"name": "Content and Posting",        "icon": "📅", "freq": "100%", "questions": [("content_strategy", "Types of content and messaging", "e.g. Product tips, customer stories, team culture, industry news; professional tone"), ("posting_schedule", "Posting frequency and schedule", "e.g. LinkedIn: daily; Twitter: 3x/day; YouTube: weekly; schedule via Buffer")]},
        {"name": "Paid and Performance",       "icon": "💰", "freq": "90%",  "questions": [("paid_strategy", "Paid social advertising plan", "e.g. LinkedIn lead gen ads $5K/month; retargeting website visitors"), ("kpis", "Performance metrics and monitoring", "e.g. Follower growth, reach, engagement rate, click-through rate, CPL")]},
    ],

    "Brand Guidelines": [
        {"name": "Brand Identity",             "icon": "🎨", "freq": "100%", "questions": [("brand_mission", "Brand mission, vision, and values", "e.g. Mission: Make enterprise docs effortless; Values: Clarity, speed, trust"), ("brand_personality", "Brand personality and tone", "e.g. Professional but approachable; smart but not arrogant; modern and clean")]},
        {"name": "Visual Identity",            "icon": "🖼️", "freq": "100%", "questions": [("colors_typography", "Color palette and typography guidelines", "e.g. Primary: #0F172A (dark) and #D4A64A (gold); Font: Inter for headings, system-ui for body"), ("logo_rules", "Logo usage rules and restrictions", "e.g. Minimum size 120px; clear space = 1× height; never distort or recolor")]},
        {"name": "Voice and Application",      "icon": "✍️", "freq": "100%", "questions": [("voice_tone", "Brand voice and messaging principles", "e.g. Write in second person; avoid jargon; lead with value not features"), ("application_examples", "Where and how brand is applied", "e.g. Website, sales decks, email signatures, social profiles, printed collateral")]},
    ],

    "Market Research Report": [
        {"name": "Market Overview",            "icon": "🌍", "freq": "100%", "questions": [("market_size", "Market size and growth trends", "e.g. Global HR tech market: $38B in 2025, growing at 11% CAGR"), ("industry_trends", "Key industry trends", "e.g. AI adoption, shift to remote work tools, compliance automation demand")]},
        {"name": "Customer and Competitor Analysis","icon":"🔍","freq":"100%","questions":[("customer_insights", "Customer behavior and needs insights", "e.g. 73% of HR managers cite manual processes as top pain point; mobile-first preference"), ("competitor_analysis", "Key competitors and their positioning", "e.g. Workday (enterprise, expensive), BambooHR (SMB), Rippling (all-in-one)")]},
        {"name": "Opportunities and Recommendations","icon":"💡","freq":"100%","questions":[("opportunities", "Market opportunities identified", "e.g. Underserved mid-market segment; no good AI-native solution below $50K/year"), ("recommendations", "Strategic recommendations based on research", "e.g. Focus on mid-market HR Directors; lead with AI automation messaging")]},
    ],

    "Press Release": [
        {"name": "Announcement Details",       "icon": "📰", "freq": "100%", "questions": [("headline", "Headline and main announcement", "e.g. DocForge AI Raises $10M Series A to Revolutionize Enterprise Document Generation"), ("announcement_details", "Key details of the announcement", "e.g. $10M led by Sequoia; will fund team expansion and product development; Q2 2026 launch")]},
        {"name": "Supporting Information",     "icon": "📋", "freq": "100%", "questions": [("quotes", "Quotes from company representatives", "e.g. CEO: 'This funding validates our vision of AI-native document automation for the enterprise'"), ("company_boilerplate", "Company background for boilerplate", "e.g. DocForge AI founded 2024; 50 customers; based in San Francisco; 25-person team")]},
    ],

    "SEO Strategy Report": [
        {"name": "Keyword Strategy",           "icon": "🔍", "freq": "100%", "questions": [("target_keywords", "Primary keywords to target", "e.g. 'HR document automation', 'AI policy generator', 'employee handbook software'"), ("keyword_rationale", "Why these keywords were selected", "e.g. High commercial intent, monthly search volumes 1K–10K, medium competition")]},
        {"name": "On-Page and Technical SEO",  "icon": "⚙️", "freq": "100%", "questions": [("onpage_strategy", "On-page SEO optimization plan", "e.g. Optimize title tags, meta descriptions, H1s, internal linking; add FAQ schema"), ("technical_issues", "Technical SEO issues identified", "e.g. Site speed 3.2s → target <2s; fix 47 broken internal links; improve mobile CLS")]},
        {"name": "Content and Backlinks",      "icon": "🔗", "freq": "100%", "questions": [("content_seo", "Content SEO strategy", "e.g. Publish 4 long-form guides/month; target featured snippets for comparison queries"), ("backlink_strategy", "Backlink acquisition strategy", "e.g. Guest posts on HR blogs; HARO responses; partner with HR associations")]},
    ],

    "Advertising Brief": [
        {"name": "Campaign Objectives",        "icon": "🎯", "freq": "100%", "questions": [("business_objective", "Business and marketing objectives", "e.g. Generate 500 demo requests in 30 days; support Q2 ARR target of $2M"), ("target_audience", "Target audience profile", "e.g. HR Directors, 30–50 years old, companies 50–500 employees, US market")]},
        {"name": "Creative Direction",         "icon": "🎨", "freq": "100%", "questions": [("core_message", "Core message and value proposition", "e.g. 'From 3 hours to 3 minutes — AI writes your HR docs'"), ("creative_direction", "Visual and creative direction", "e.g. Clean, dark minimal aesthetic; show before/after of manual vs AI generation; no stock photos")]},
        {"name": "Budget and Deliverables",    "icon": "💰", "freq": "100%", "questions": [("budget", "Campaign budget allocation by channel", "e.g. Total $30K: Google Search $15K, LinkedIn $10K, Retargeting $5K"), ("deliverables", "Expected creative deliverables", "e.g. 3 video ads (15s), 6 static display ads, 4 LinkedIn carousel ads, 2 landing pages")]},
    ],

    "Email Campaign Plan": [
        {"name": "Campaign Objectives",        "icon": "📧", "freq": "100%", "questions": [("campaign_goal", "Campaign goal and target audience", "e.g. Nurture trial users to convert to paid — targeting 2,000 free tier users"), ("email_themes", "Email content themes", "e.g. Value demonstration, use case education, social proof, urgency-based CTA")]},
        {"name": "Sequence and Automation",    "icon": "🔄", "freq": "100%", "questions": [("email_sequence", "Email schedule and automation workflow", "e.g. Day 1: Welcome; Day 3: Feature tip; Day 7: Case study; Day 14: Upgrade CTA"), ("personalization", "Personalization and segmentation strategy", "e.g. Segment by role (HR/Legal/Finance); personalize subject line with first name and company")]},
        {"name": "Metrics and Compliance",     "icon": "📊", "freq": "100%", "questions": [("kpis", "Target metrics", "e.g. Open rate >40%, CTR >5%, trial-to-paid conversion >15%"), ("compliance", "Compliance and opt-in policies", "e.g. CAN-SPAM and GDPR compliant; all recipients opted in; unsubscribe in every email")]},
    ],

    "Influencer Agreement": [
        {"name": "Collaboration Scope",        "icon": "🤳", "freq": "100%", "questions": [("influencer_info", "Influencer name, platform and audience", "e.g. @TechWithSarah — LinkedIn, 85K followers, HR and Future of Work niche"), ("deliverables", "Content deliverables and requirements", "e.g. 2 LinkedIn posts, 1 video review, 1 story mention; must include product demo")]},
        {"name": "Payment and IP",             "icon": "💰", "freq": "100%", "questions": [("compensation", "Compensation and payment terms", "e.g. $3,500 flat fee; 50% upfront, 50% after content approval"), ("content_rights", "Intellectual property and usage rights", "e.g. Company may repurpose content for 12 months; influencer retains copyright")]},
        {"name": "Compliance and Terms",       "icon": "⚖️", "freq": "100%", "questions": [("disclosure", "Disclosure and advertising compliance", "e.g. Must include #ad and #sponsored on all posts; follow FTC guidelines"), ("termination", "Termination and dispute conditions", "e.g. Company may terminate if content is not delivered within 14 days of agreed date")]},
    ],

    # ── IT ────────────────────────────────────────────────────────────────────

    "IT Access Request Form": [
        {"name": "Access Request Details",     "icon": "🔐", "freq": "100%", "questions": [("systems_requested", "Systems or applications access is needed for", "e.g. AWS Console, GitHub org, Jira, Notion workspace, PagerDuty"), ("access_level", "Level of access required", "e.g. Admin access to AWS us-east-1; read-only Jira; editor Notion")]},
        {"name": "Purpose and Duration",       "icon": "📋", "freq": "100%", "questions": [("purpose", "Business reason for access", "e.g. New hire joining DevOps team; needs access for day-to-day infrastructure work"), ("duration", "Temporary or permanent; if temporary, how long", "e.g. Permanent access for employment duration")]},
        {"name": "Security Confirmation",      "icon": "🛡️", "freq": "100%", "questions": [("security_acknowledgment", "Security responsibilities acknowledged", "e.g. Will use MFA; will not share credentials; will follow least-privilege principle"), ("manager_approval", "Approving manager and authorization", "e.g. Approved by: Sarah Kim, VP Engineering")]},
    ],

    "Incident Report": [
        {"name": "Incident Description",       "icon": "🚨", "freq": "100%", "questions": [("incident_description", "What happened — full description of the incident", "e.g. Database connection pool exhausted at 2:15pm; application returned 503 errors to all users"), ("affected_systems", "Systems and services impacted", "e.g. Production API, customer dashboard, Stripe webhooks; 3,200 users affected")]},
        {"name": "Timeline and Impact",        "icon": "⏱️", "freq": "100%", "questions": [("timeline", "Timeline of incident detection and resolution", "e.g. 14:15 detected; 14:22 incident declared; 14:55 fix deployed; 15:10 fully resolved"), ("impact", "Business and user impact", "e.g. 55 minutes of degraded service; ~120 failed transactions; 14 customer complaints")]},
        {"name": "Root Cause and Prevention",  "icon": "🔍", "freq": "100%", "questions": [("root_cause", "Root cause analysis", "e.g. New deployment increased query concurrency without updating connection pool size"), ("preventive_measures", "Actions to prevent recurrence", "e.g. Add pool size to deployment checklist; implement connection pool monitoring alert")]},
    ],

    "System Maintenance Report": [
        {"name": "Maintenance Activities",     "icon": "🔧", "freq": "100%", "questions": [("system_id", "System and maintenance schedule", "e.g. Production Kubernetes cluster — scheduled maintenance March 15, 2026 02:00–04:00 UTC"), ("activities", "Maintenance activities performed", "e.g. Node OS patches (CVE-2026-1234), k8s upgrade 1.28→1.29, certificate renewal")]},
        {"name": "Issues and Outcomes",        "icon": "📊", "freq": "100%", "questions": [("issues_found", "Issues identified during maintenance", "e.g. Found 2 nodes with failing disk health; 1 outdated TLS certificate missed in scan"), ("post_maintenance", "System performance after maintenance", "e.g. All services healthy; response time improved 12%; no open critical alerts")]},
    ],

    "Software Installation Request": [
        {"name": "Software Details",           "icon": "💻", "freq": "100%", "questions": [("software_name", "Software name, version, and vendor", "e.g. DataGrip v2025.1 by JetBrains — database IDE"), ("business_need", "Business need and justification", "e.g. Needed for database debugging and query optimization; replaces manual psql scripts")]},
        {"name": "Compliance Checks",          "icon": "✅", "freq": "100%", "questions": [("license_check", "License availability and cost", "e.g. Team license available; $199/seat/year; budget approved by Finance"), ("security_review", "Security and compatibility assessment", "e.g. Reviewed against software whitelist; no known CVEs; macOS 14 compatible")]},
    ],

    "Data Backup Policy": [
        {"name": "Backup Scope and Schedule",  "icon": "💾", "freq": "100%", "questions": [("data_scope", "Data covered by this backup policy", "e.g. All production databases, user files, configuration data, application secrets"), ("backup_schedule", "Backup frequency and retention", "e.g. Hourly snapshots (24h retention), daily full backups (30-day retention), weekly archives (1-year retention)")]},
        {"name": "Storage and Security",       "icon": "🔒", "freq": "100%", "questions": [("storage_locations", "Where backups are stored", "e.g. Primary: AWS S3 us-east-1; Secondary: AWS S3 eu-west-1; both encrypted AES-256"), ("access_control", "Who can access backups and how", "e.g. Only DevOps team with MFA; access logged in SIEM; quarterly access review")]},
        {"name": "Restoration and Compliance", "icon": "🔄", "freq": "100%", "questions": [("restoration", "Restoration procedures and RTO/RPO targets", "e.g. RTO: 4 hours; RPO: 1 hour; tested monthly via automated restore verification"), ("compliance", "Compliance and regulatory requirements", "e.g. SOC 2 CC6.1; GDPR Article 32; backup tested annually as part of DR exercise")]},
    ],

    "Security Incident Report": [
        {"name": "Incident Description",       "icon": "🔴", "freq": "100%", "questions": [("incident_type", "Type of security incident", "e.g. Phishing attack — employee credentials compromised; unauthorized access to email"), ("affected_scope", "Systems or data affected", "e.g. One employee Gmail account; no access to production systems; possible exposure of 3 internal emails")]},
        {"name": "Response and Investigation", "icon": "🔍", "freq": "100%", "questions": [("response_actions", "Immediate response actions taken", "e.g. Account suspended within 10 min; password reset; MFA enforced; email forwarding rules removed"), ("investigation", "Investigation findings", "e.g. Attacker from Russian IP; accessed email 4 hours before detection; no lateral movement detected")]},
        {"name": "Remediation and Reporting",  "icon": "🛡️", "freq": "100%", "questions": [("corrective_actions", "Corrective actions and security improvements", "e.g. Security awareness training for all staff; phishing simulation program started; conditional access policies added"), ("reporting_requirements", "Compliance and regulatory reporting needed", "e.g. GDPR breach notification to DPA within 72 hours; customers notified if data impacted")]},
    ],

    "IT Asset Allocation Form": [
        {"name": "Asset Details",              "icon": "💻", "freq": "100%", "questions": [("asset_info", "Asset details and ID number", "e.g. MacBook Pro 16\" M3 — S/N: C02XY1234 — Asset ID: ASSET-2026-0142"), ("asset_condition", "Condition at time of allocation", "e.g. New — unopened box; battery health 100%; no scratches")]},
        {"name": "Allocation Details",         "icon": "👤", "freq": "100%", "questions": [("employee_info", "Employee receiving the asset", "e.g. Emma Wilson, Junior Developer, Engineering team, start date April 1, 2026"), ("usage_responsibilities", "Usage rules and return conditions", "e.g. For company use only; keep in protective case; return on employment end in same condition")]},
    ],

    "Network Access Agreement": [
        {"name": "Access Scope and Policies",  "icon": "🌐", "freq": "100%", "questions": [("network_scope", "Scope of network access granted", "e.g. Access to corporate VPN, internal tools, and cloud infrastructure; no production DB direct access"), ("acceptable_use", "Acceptable use policy", "e.g. For business purposes only; personal use limited; no streaming or torrenting")]},
        {"name": "Security and Monitoring",    "icon": "🔒", "freq": "100%", "questions": [("security_responsibilities", "User security obligations", "e.g. Use VPN on public wifi; do not split tunnel; report suspicious activity immediately"), ("monitoring", "Monitoring and compliance statement", "e.g. All network activity may be monitored; violation results in immediate access revocation")]},
    ],

    "Software License Report": [
        {"name": "License Inventory",          "icon": "📋", "freq": "100%", "questions": [("software_inventory", "List of licensed software and seat counts", "e.g. Slack (250 seats), GitHub Teams (45 seats), Figma (20 seats), Zoom (250 seats)"), ("license_types", "License types and expiry dates", "e.g. Slack: annual, expires Dec 2026; GitHub: monthly; Figma: annual, expires Oct 2026")]},
        {"name": "Compliance and Cost",        "icon": "💰", "freq": "100%", "questions": [("compliance_status", "License compliance status", "e.g. All tools compliant; 10 Figma seats unused — recommend downgrade"), ("cost_analysis", "Annual license costs and optimization opportunities", "e.g. Total annual spend: $185,000; can save $12K by eliminating unused seats")]},
    ],

    "System Upgrade Proposal": [
        {"name": "Current System and Problem", "icon": "⚠️", "freq": "100%", "questions": [("current_system", "Current system and its limitations", "e.g. PostgreSQL 11 on EC2 — end-of-life Nov 2026; no native vector search; performance bottlenecks at >1M rows"), ("upgrade_purpose", "Purpose and justification for upgrade", "e.g. Security compliance, AI feature support, 3× query performance improvement")]},
        {"name": "Proposed Solution",          "icon": "💡", "freq": "100%", "questions": [("proposed_upgrade", "Proposed upgrade solution and requirements", "e.g. Migrate to PostgreSQL 16 on RDS with pgvector extension; Multi-AZ deployment"), ("timeline_cost", "Implementation timeline and estimated cost", "e.g. 6-week migration plan; $3,200/month RDS cost vs $2,100 current — ROI in 4 months via performance gains")]},
    ],

    # ── Operations ────────────────────────────────────────────────────────────

    "Standard Operating Procedure (SOP)": [
        {"name": "Purpose and Scope",          "icon": "🎯", "freq": "100%", "questions": [("purpose", "Why this SOP exists and what it covers", "e.g. Ensure consistent and compliant customer data handling across all support channels"), ("scope", "Departments, processes, and people covered", "e.g. Applies to all Customer Support agents handling personal data requests")]},
        {"name": "Step-by-Step Procedure",     "icon": "📋", "freq": "100%", "questions": [("steps", "Sequential steps to complete the procedure", "e.g. 1. Verify customer identity; 2. Log request in ticketing system; 3. Retrieve data; 4. Deliver within 30 days"), ("tools_required", "Tools, systems, or equipment needed", "e.g. Zendesk, Postgres admin access, secure file transfer tool")]},
        {"name": "Roles and Quality Control",  "icon": "👥", "freq": "100%", "questions": [("roles", "Who is responsible for each step", "e.g. Agent: steps 1–3; Supervisor: step 4 approval; DPO: final sign-off on sensitive requests"), ("quality_compliance", "Quality standards and compliance checks", "e.g. GDPR Article 12 — 30-day response time; log all requests in compliance tracker")]},
        {"name": "Exception Handling",         "icon": "⚠️", "freq": "95%",  "questions": [("exceptions", "How to handle deviations from standard process", "e.g. If verification fails, escalate to fraud team before proceeding"), ("escalation", "Escalation path for complex situations", "e.g. Escalate to DPO if request involves special category data")]},
    ],

    "Operations Report": [
        {"name": "Operations Overview",        "icon": "📊", "freq": "100%", "questions": [("reporting_period", "Reporting period and operational scope", "e.g. Q1 2026 — Logistics and Fulfillment Operations"), ("key_metrics", "Key operational metrics and performance", "e.g. On-time delivery: 94%; Order processing time: avg 2.1 days; Defect rate: 0.8%")]},
        {"name": "Challenges and Improvements","icon":"⚙️","freq":"100%","questions":[("challenges", "Operational challenges encountered", "e.g. Warehouse staff shortage in February caused 3-day delay; supplier X late on 8 orders"), ("improvements", "Improvements implemented this period", "e.g. Automated order routing reduced processing time by 30%; new SLA with supplier Y")]},
        {"name": "Recommendations",            "icon": "💡", "freq": "95%",  "questions": [("recommendations", "Actions to improve performance next period", "e.g. Hire 3 warehouse associates; implement barcode scanning for all outbound orders"), ("next_period_focus", "Focus areas for next reporting period", "e.g. Reduce defect rate to <0.5%; implement real-time inventory tracking")]},
    ],

    "Process Improvement Plan": [
        {"name": "Current Process Analysis",   "icon": "🔍", "freq": "100%", "questions": [("current_process", "Description of current process and its issues", "e.g. Manual invoice approval: 3 people, 5 days avg — causing payment delays and vendor complaints"), ("root_causes", "Root causes of process inefficiency", "e.g. No automated routing; approvers not notified promptly; no SLA tracking")]},
        {"name": "Proposed Improvements",      "icon": "💡", "freq": "100%", "questions": [("improvements", "Specific process changes proposed", "e.g. Implement automated invoice routing in NetSuite; auto-escalation after 48h; mobile approval app"), ("expected_outcomes", "Expected results and measurable benefits", "e.g. Reduce approval time from 5 days to 1 day; eliminate 2 FTE manual steps; 95% on-time payment")]},
        {"name": "Implementation and Timeline","icon":"📅","freq":"100%","questions":[("implementation_plan", "How changes will be rolled out", "e.g. Phase 1: NetSuite config (2 weeks); Phase 2: Training (1 week); Phase 3: Go-live (1 week)"), ("success_metrics", "How success will be measured", "e.g. Invoice cycle time, payment on-time rate, vendor satisfaction score")]},
    ],

    "Risk Assessment Report": [
        {"name": "Risk Identification",        "icon": "⚠️", "freq": "100%", "questions": [("scope", "Scope and area of risk assessment", "e.g. Q2 2026 product launch — technical, operational, and commercial risks"), ("risks_identified", "Key risks identified", "e.g. 1. Integration delays (technical); 2. Competitor launches same week; 3. Insufficient support staffing")]},
        {"name": "Risk Analysis and Mitigation","icon":"🛡️","freq":"100%","questions":[("risk_analysis", "Probability and impact of each risk", "e.g. Integration delays: High probability (60%), High impact — could delay launch 4 weeks"), ("mitigation", "Mitigation strategies for top risks", "e.g. Add 2 contract engineers; initiate launch date flexibility; cross-train 5 support agents")]},
        {"name": "Monitoring and Review",      "icon": "📊", "freq": "100%", "questions": [("monitoring", "How risks will be monitored", "e.g. Weekly risk review in Engineering standup; risk register updated every Friday"), ("review_cadence", "Review schedule", "e.g. Full risk assessment review monthly; escalation to exec team for any High/High risks")]},
    ],

    "Inventory Report": [
        {"name": "Inventory Summary",          "icon": "📦", "freq": "100%", "questions": [("reporting_period", "Reporting period and inventory scope", "e.g. February 2026 — Warehouse B, Electronics category"), ("stock_summary", "Current stock quantities by category", "e.g. Laptops: 45 units; Monitors: 62 units; Accessories: 210 units; Total value: $87,500")]},
        {"name": "Movements and Issues",       "icon": "🔄", "freq": "100%", "questions": [("movements", "Inventory movements — received and dispatched", "e.g. Received: 30 laptops; Dispatched: 18 laptops; Net change: +12 units"), ("discrepancies", "Stock discrepancies or low-stock alerts", "e.g. 3 monitors missing vs records (investigation opened); keyboards at reorder point — order needed")]},
    ],

    "Production Plan": [
        {"name": "Production Objectives",      "icon": "🏭", "freq": "100%", "questions": [("product_specs", "Products to be produced and specifications", "e.g. Model X Widget — 10,000 units; Model Y Widget — 5,000 units; Q2 2026"), ("volume_targets", "Production volume targets and schedule", "e.g. 750 units/day; 5-day work week; completion by June 30, 2026")]},
        {"name": "Resources and Quality",      "icon": "⚙️", "freq": "100%", "questions": [("resources", "Labor, equipment, and material requirements", "e.g. 45 production staff, 3 assembly lines, raw materials PO already raised"), ("quality_control", "Quality control measures", "e.g. 100% QC inspection on final assembly; 5% random sample mid-production; reject rate target <1%")]},
    ],

    "Logistics Plan": [
        {"name": "Transportation and Delivery","icon":"🚚","freq":"100%","questions":[("transport_strategy", "Transportation modes and carriers", "e.g. Domestic: FedEx Ground; International: DHL Express; air freight for urgent orders only"), ("delivery_schedule", "Delivery scheduling and lead times", "e.g. Standard 3–5 business days domestic; 7–10 days international; same-day available in metro areas")]},
        {"name": "Warehouse and Cost",         "icon": "🏭", "freq": "100%", "questions": [("warehouse_plan", "Warehouse and storage plan", "e.g. Primary warehouse: Dallas TX (60% capacity); overflow: Atlanta GA; 3PL used for peak season"), ("cost_management", "Logistics cost management strategy", "e.g. Rate shopping via EasyPost; zone skipping for large volumes; bulk FedEx contract saves 18%")]},
    ],

    "Supplier Evaluation Report": [
        {"name": "Evaluation Criteria",        "icon": "📋", "freq": "100%", "questions": [("supplier_name", "Supplier name and evaluation period", "e.g. SupplyCo Ltd — Annual evaluation, FY2025"), ("evaluation_criteria", "Criteria used for evaluation", "e.g. Quality (30%), Delivery (25%), Price (25%), Compliance (10%), Communication (10%)")]},
        {"name": "Performance Assessment",     "icon": "📊", "freq": "100%", "questions": [("performance_scores", "Scores and findings for each criterion", "e.g. Quality: 4/5 (2 defect incidents); Delivery: 3/5 (4 late deliveries); Price: 5/5 (below market)"), ("recommendation", "Overall rating and recommendation", "e.g. Overall: Acceptable (3.7/5); Recommend retaining with mandatory quality improvement plan")]},
    ],

    "Quality Control Checklist": [
        {"name": "Inspection Criteria",        "icon": "🔍", "freq": "100%", "questions": [("product_process", "Product or process being inspected", "e.g. Mobile app build v2.4.1 — pre-release QA inspection"), ("inspection_criteria", "Quality inspection criteria and standards", "e.g. All critical bugs resolved; performance <3s load; accessibility WCAG 2.1 AA; security OWASP Top 10 clear")]},
        {"name": "Results and Actions",        "icon": "📋", "freq": "100%", "questions": [("inspection_results", "Results of quality inspection", "e.g. 2 critical bugs found (login crash on iOS 17); 5 minor UI issues; performance: 2.1s (pass)"), ("corrective_actions", "Corrective actions required before approval", "e.g. Fix 2 critical bugs; retest; minor UI issues logged for v2.4.2")]},
    ],

    "Business Continuity Plan": [
        {"name": "Critical Functions and Risks","icon":"🏢","freq":"100%","questions":[("critical_functions", "Critical business functions that must be maintained", "e.g. Customer API service, payment processing, customer support — all must maintain 99.9% availability"), ("risk_threats", "Key risks and threats addressed by this plan", "e.g. Data center outage, cybersecurity attack, key personnel unavailability, supply chain disruption")]},
        {"name": "Recovery Strategy",          "icon": "🔄", "freq": "100%", "questions": [("recovery_procedures", "Recovery procedures for each critical function", "e.g. API: auto-failover to secondary region in <5 min; Payments: Stripe fallback activated automatically"), ("rto_rpo", "Recovery time and recovery point objectives", "e.g. RTO: 4 hours for full recovery; RPO: 1 hour maximum data loss")]},
        {"name": "Communication and Testing",  "icon": "📡", "freq": "100%", "questions": [("communication_plan", "Communication plan during disruptions", "e.g. Status page updated within 15 min; email to customers >30 min outage; Slack #incidents for team"), ("testing_schedule", "BCP testing and review schedule", "e.g. Full DR drill twice annually; tabletop exercises quarterly; plan reviewed annually")]},
    ],

    # ── Customer Support ──────────────────────────────────────────────────────

    "Support Ticket Report": [
        {"name": "Issue Description",          "icon": "🎫", "freq": "100%", "questions": [("issue_description", "Full description of the customer's issue", "e.g. Customer unable to log in after password reset; receiving 'invalid token' error on all devices"), ("affected_product", "Product or service affected", "e.g. DocForge AI web app — authentication module, all users on Enterprise plan")]},
        {"name": "Troubleshooting and Resolution","icon":"🔧","freq":"100%","questions":[("troubleshooting", "Troubleshooting steps taken", "e.g. Verified account status, cleared token cache, re-sent password reset link, checked SSO config"), ("resolution", "Resolution summary", "e.g. Identified expired SAML certificate; renewed cert; customer confirmed login working 14:35")]},
        {"name": "Closure Details",            "icon": "✅", "freq": "100%", "questions": [("resolution_time", "Time from open to close", "e.g. Opened 13:10; resolved 14:35 — 1 hour 25 min resolution time"), ("customer_confirmation", "Customer satisfaction confirmation", "e.g. Customer replied 'all working now, thank you' — ticket closed 14:40")]},
    ],

    "Customer Complaint Report": [
        {"name": "Complaint Description",      "icon": "😤", "freq": "100%", "questions": [("complaint", "Detailed description of customer complaint", "e.g. Customer claims document generation failed 3 times, losing 4 hours of work — demands credit"), ("customer_impact", "Impact on customer experience", "e.g. Significant disruption to HR team's quarterly review preparation; customer considering cancellation")]},
        {"name": "Investigation and Resolution","icon":"🔍","freq":"100%","questions":[("investigation", "Investigation findings", "e.g. Found bug in document assembly step for docs >5,000 words — patched in v2.3.2 deployed March 14"), ("resolution", "Corrective actions and resolution outcome", "e.g. Bug fixed; customer issued $500 service credit; account manager to check in weekly for 30 days")]},
        {"name": "Improvement Recommendations","icon":"💡","freq":"90%","questions":[("recommendations", "Service improvement recommendations", "e.g. Add auto-save every 60 seconds; improve error messages; add progress indicator for long docs"), ("management_review", "Management notes or decisions", "e.g. Engineering priority ticket raised; customer retention offer approved by Customer Success VP")]},
    ],

    "Customer Feedback Report": [
        {"name": "Feedback Summary",           "icon": "📊", "freq": "100%", "questions": [("collection_method", "How feedback was collected and period", "e.g. In-app NPS survey — Q1 2026 — 450 responses (22% response rate); NPS score: 52"), ("positive_feedback", "Highlights of positive feedback", "e.g. 78% rated document quality as 'excellent'; AI speed praised by 65% of respondents")]},
        {"name": "Issues and Recommendations", "icon": "💡", "freq": "100%", "questions": [("negative_feedback", "Common complaints and concerns", "e.g. 35% mentioned slow generation for complex documents; 28% want more templates"), ("recommendations", "Recommended actions based on feedback", "e.g. Optimize LLM calls for >8 section docs; add 20 new templates for Legal category in Q2")]},
    ],

    "SLA Agreement": [
        {"name": "Service Scope and Availability","icon":"📋","freq":"100%","questions":[("services_covered", "Services covered by this SLA", "e.g. DocForge AI API, web application, Notion integration, customer support"), ("availability", "Uptime commitment and scheduled maintenance", "e.g. 99.9% uptime (max 8.7 hours downtime/year); planned maintenance Sundays 02:00–04:00 UTC with 48h notice")]},
        {"name": "Response and Resolution Times","icon":"⏱️","freq":"100%","questions":[("response_times", "Response time standards by priority", "e.g. P1 Critical: 15 min response, 2hr resolution; P2 High: 1hr/8hr; P3 Medium: 4hr/24hr; P4 Low: 24hr/72hr"), ("escalation", "Escalation procedures", "e.g. P1 auto-pages on-call engineer + manager; P2 escalates after 4hr; customer receives status updates every 30 min for P1")]},
        {"name": "Credits and Monitoring",     "icon": "💰", "freq": "100%", "questions": [("service_credits", "Service credits for SLA breaches", "e.g. 99.9%–99%: 10% monthly credit; 99%–95%: 25% credit; <95%: 50% credit; applied to next invoice"), ("monitoring", "How SLA performance is tracked and reported", "e.g. Uptime monitored via Datadog and Pingdom; monthly SLA report emailed to customer by 5th of each month")]},
    ],

    "Support Resolution Report": [
        {"name": "Problem and Diagnosis",      "icon": "🔍", "freq": "100%", "questions": [("issue_summary", "Summary of the problem", "e.g. Customer's Notion integration stopped syncing documents after workspace was renamed"), ("diagnosis", "Root cause diagnosis", "e.g. Notion API token was scoped to specific workspace ID which changed on rename; auth failure")]},
        {"name": "Resolution and Prevention",  "icon": "✅", "freq": "100%", "questions": [("resolution_steps", "Steps taken to resolve the issue", "e.g. Re-authorized Notion integration with new workspace ID; tested sync with 5 documents — all successful"), ("preventive_recommendations", "Recommendations to prevent recurrence", "e.g. Add integration health checks; alert customer before token expiry; update help docs on workspace settings")]},
    ],

    "Customer Escalation Report": [
        {"name": "Escalation Reason",          "icon": "🔺", "freq": "100%", "questions": [("escalation_reason", "Why the issue was escalated", "e.g. Customer Acme Corp threatening churn after 3 unresolved incidents in 30 days; involves $120K contract"), ("previous_attempts", "Previous resolution attempts", "e.g. Ticket #4421 (resolved Day 1), #4455 (workaround provided), #4488 (unresolved after 5 days)")]},
        {"name": "Resolution and Outcome",     "icon": "✅", "freq": "100%", "questions": [("corrective_actions", "Actions taken to resolve escalation", "e.g. Assigned dedicated senior engineer; root cause fixed in hotfix v2.3.4; 3-month credit offered"), ("customer_outcome", "Final resolution and customer status", "e.g. Customer satisfied — confirmed no churn intent; account review scheduled with CSM and VP Sales")]},
    ],

    "Service Improvement Plan": [
        {"name": "Current Performance Issues","icon":"📊","freq":"100%","questions":[("current_performance", "Current service performance and identified issues", "e.g. CSAT: 72% (target 85%); avg first response: 6 hours (SLA: 4 hours); 15% ticket re-open rate"), ("root_causes", "Root causes of service gaps", "e.g. Insufficient Tier 1 staff; knowledge base outdated; complex tickets mis-routed")]},
        {"name": "Improvement Initiatives",   "icon": "💡", "freq": "100%", "questions": [("initiatives", "Proposed improvement initiatives", "e.g. Hire 3 Tier 1 agents; revamp 50 top KB articles; implement AI-assisted ticket routing"), ("timeline", "Implementation timeline and milestones", "e.g. Hiring complete by April 15; KB overhaul by May 1; routing AI live by May 15; CSAT target 85% by June 30")]},
    ],

    "Customer Onboarding Guide": [
        {"name": "Product Overview and Setup","icon":"🚀","freq":"100%","questions":[("product_overview", "Overview of the product or service", "e.g. DocForge AI is your AI-powered document generation platform — create enterprise docs in minutes"), ("setup_steps", "Account setup and getting started steps", "e.g. 1. Verify email; 2. Complete company profile; 3. Connect Notion; 4. Generate first document")]},
        {"name": "Resources and Support",     "icon": "📚", "freq": "100%", "questions": [("training_resources", "Training and learning resources available", "e.g. Video library at help.docforge.ai; live onboarding webinar Tuesdays 2pm; in-app tooltips"), ("support_info", "Support channels and tips for success", "e.g. Chat support in-app (business hours); email support@docforge.ai; community forum")]},
    ],

    "FAQ Document": [
        {"name": "Core Product FAQs",         "icon": "❓", "freq": "100%", "questions": [("product_faqs", "Most common product and feature questions", "e.g. What document types can I generate? How accurate is the AI? Can I edit generated docs?"), ("account_faqs", "Common account and access questions", "e.g. How do I invite team members? What happens if I exceed my plan limit? How do I reset my password?")]},
        {"name": "Billing and Support FAQs",  "icon": "💳", "freq": "100%", "questions": [("billing_faqs", "Billing, payment, and plan questions", "e.g. What payment methods are accepted? Can I change plans mid-cycle? Is there a free trial?"), ("support_faqs", "Support, troubleshooting, and security questions", "e.g. How do I contact support? Where is my data stored? Is my data used to train AI models?")]},
    ],

    "Support Training Manual": [
        {"name": "Support Standards",         "icon": "🎓", "freq": "100%", "questions": [("service_standards", "Customer service standards and KPIs", "e.g. First response <4hr; CSAT >85%; resolution rate >90%; professional and empathetic tone always"), ("communication_guidelines", "Communication best practices", "e.g. Acknowledge, empathize, own, resolve (AEOR framework); never say 'I don't know' — always escalate")]},
        {"name": "Ticket Handling Procedures","icon":"📋","freq":"100%","questions":[("ticket_procedures", "Ticket creation, routing, and handling steps", "e.g. 1. Log in Zendesk; 2. Apply correct tag and priority; 3. Reply within SLA; 4. Document all actions taken"), ("escalation_guide", "Escalation criteria and procedures", "e.g. Escalate to Tier 2 if: no resolution in 2 hours; customer threatens churn; involves data security")]},
        {"name": "Difficult Situations",      "icon": "😤", "freq": "95%",  "questions": [("difficult_scenarios", "How to handle difficult customer situations", "e.g. Angry customer: stay calm, don't argue, acknowledge, offer concrete solution; never match their tone"), ("quality_evaluation", "Performance evaluation criteria", "e.g. Monthly CSAT score, ticket volume, first contact resolution rate, peer review scores")]},
    ],

    # ── Procurement ───────────────────────────────────────────────────────────

    "Vendor Registration Form": [
        {"name": "Vendor Basic Information",  "icon": "🏭", "freq": "100%", "questions": [("vendor_details", "Company name, type, and contact info", "e.g. Tech Supplies Ltd — IT Hardware Distributor — contact@techsupplies.com — +1-800-555-0100"), ("business_registration", "Registration number, tax ID, and legal status", "e.g. Reg #: TX-2019-12345; EIN: 45-6789012; Incorporated in Texas, USA")]},
        {"name": "Services and Compliance",   "icon": "📋", "freq": "100%", "questions": [("products_services", "Products or services offered", "e.g. Enterprise laptops, monitors, accessories, on-site warranty service"), ("certifications", "Licenses, certifications, and compliance", "e.g. ISO 9001:2015 certified; authorized Apple reseller; GDPR compliant; references available on request")]},
        {"name": "Financial and Documents",   "icon": "💰", "freq": "100%", "questions": [("bank_details", "Bank account and payment preferences", "e.g. Wells Fargo — Acct #123456789 — ACH preferred; Net 30 standard terms"), ("supporting_docs", "Documents submitted for registration", "e.g. Certificate of incorporation, tax clearance, ISO certificate, 3 client references")]},
    ],

    "Vendor Evaluation Report": [
        {"name": "Evaluation Criteria",       "icon": "📊", "freq": "100%", "questions": [("vendor_name", "Vendor name and evaluation period", "e.g. CloudHost Inc — Q1 2026 quarterly evaluation"), ("criteria", "Evaluation criteria and weights", "e.g. Quality 30%, Delivery 25%, Price 20%, Compliance 15%, Support 10%")]},
        {"name": "Performance Scores",        "icon": "⭐", "freq": "100%", "questions": [("scores", "Scores and findings per criterion", "e.g. Quality: 5/5 (zero defects); Delivery: 4/5 (1 minor delay); Price: 4/5 (competitive); Compliance: 5/5"), ("recommendation", "Overall rating and engagement recommendation", "e.g. Overall: 4.5/5 — Highly Recommended; propose 2-year contract renewal with 5% price lock")]},
    ],

    "Purchase Requisition": [
        {"name": "Item and Justification",    "icon": "📦", "freq": "100%", "questions": [("item_description", "Item or service description and quantity", "e.g. 15 × Ergonomic office chairs (model: Herman Miller Aeron); required for new hire cohort"), ("justification", "Business justification and budget", "e.g. Mandatory ergonomic setup per company health policy; $15,000 budgeted in office supplies Q2")]},
        {"name": "Approval Details",          "icon": "✅", "freq": "100%", "questions": [("delivery_date", "Required delivery date", "e.g. Needed by April 15, 2026 — new hires join April 1"), ("approval_info", "Manager and budget approval details", "e.g. Approved by: Maria Chen, Operations Director; budget confirmed by Finance 2026-03-10")]},
    ],

    "Procurement Plan": [
        {"name": "Procurement Objectives",    "icon": "🎯", "freq": "100%", "questions": [("objectives", "Procurement goals and strategy", "e.g. Procure all Q2 technology infrastructure at minimum 10% below market rate within 60 days"), ("scope", "Scope of procurement activities", "e.g. Cloud infrastructure, endpoint devices, cybersecurity tools, facilities management")]},
        {"name": "Budget and Supplier Strategy","icon":"💰","freq":"100%","questions":[("budget", "Budget allocation by category", "e.g. Cloud: $120K, Devices: $80K, Security: $45K, Facilities: $30K — Total: $275K"), ("supplier_criteria", "Supplier selection criteria", "e.g. Must be ISO 27001; min 3 years in operation; references from 2 comparable companies required")]},
        {"name": "Schedule and Compliance",   "icon": "📅", "freq": "100%", "questions": [("schedule", "Procurement schedule and key milestones", "e.g. RFP out April 1; vendor selection April 15; contracts signed April 30; delivery May 31"), ("compliance_requirements", "Policy and regulatory compliance", "e.g. All vendors must complete GDPR due diligence; contracts reviewed by Legal before signing")]},
    ],

    "Bid Evaluation Report": [
        {"name": "Bid Summary",               "icon": "📋", "freq": "100%", "questions": [("procurement_ref", "Procurement reference and participating vendors", "e.g. RFP-2026-IT-004 — Cloud Infrastructure; 4 bids received: AWS, Azure, GCP, Oracle"), ("evaluation_criteria", "Evaluation criteria and weights", "e.g. Technical: 40%, Price: 35%, Compliance: 15%, Support: 10%")]},
        {"name": "Evaluation Results",        "icon": "🏆", "freq": "100%", "questions": [("scores", "Technical and financial evaluation scores", "e.g. AWS: 88/100 (Tech: 36/40, Price: 32/35, Compliance: 13/15, Support: 7/10)"), ("recommendation", "Recommended vendor selection and rationale", "e.g. Recommend AWS — highest overall score; existing tooling integration; best pricing for 3-year commitment")]},
    ],

    "Supplier Risk Assessment": [
        {"name": "Risk Analysis",             "icon": "⚠️", "freq": "100%", "questions": [("supplier_name", "Supplier name and assessment scope", "e.g. Global Parts Co — primary PCB supplier for Product Line A"), ("risks_identified", "Key risks identified across categories", "e.g. Financial: high debt ratio; Operational: single factory in Taiwan; Geopolitical: Taiwan Strait risk; Compliance: REACH certification pending")]},
        {"name": "Risk Mitigation",           "icon": "🛡️", "freq": "100%", "questions": [("risk_ratings", "Risk ratings for each category", "e.g. Financial: Medium (3/5); Operational: High (4/5); Geopolitical: High (4/5); Compliance: Low (2/5)"), ("mitigation_strategies", "Risk mitigation strategies", "e.g. Qualify secondary supplier in Vietnam by Q3; increase safety stock to 90 days; quarterly financial monitoring")]},
    ],

    "Contract Renewal Notice": [
        {"name": "Renewal Details",           "icon": "🔄", "freq": "100%", "questions": [("existing_contract", "Reference to existing contract and expiry", "e.g. Vendor Agreement VA-2024-077 with SupplyCo Ltd — expires March 31, 2026"), ("renewal_terms", "Updated terms for renewal period", "e.g. Price adjustment: +3% CPI increase; scope expanded to include new warehouse locations")]},
        {"name": "Response Requirements",     "icon": "📋", "freq": "100%", "questions": [("renewal_duration", "Proposed renewal period", "e.g. 12-month renewal: April 1, 2026 – March 31, 2027"), ("vendor_response", "What vendor must do and by when", "e.g. Confirm acceptance or propose changes by March 20, 2026; email: procurement@company.com")]},
    ],

    "Delivery Acceptance Report": [
        {"name": "Delivery and Inspection",   "icon": "📦", "freq": "100%", "questions": [("delivery_details", "Purchase order and delivery details", "e.g. PO-2026-0110 — 20 MacBook Pro 14\" — delivered March 15, 2026 by FedEx"), ("inspection_results", "Quantity and quality inspection results", "e.g. 20 units received; all sealed in original packaging; spot-check of 5 units — all passed")]},
        {"name": "Discrepancies and Acceptance","icon":"✅","freq":"100%","questions":[("discrepancies", "Any discrepancies or issues identified", "e.g. 1 unit had cracked screen protector (cosmetic only) — noted but accepted; vendor notified"), ("acceptance_confirmation", "Formal acceptance confirmation", "e.g. Delivery accepted in full; signed by: Mark Johnson, IT Manager, March 15, 2026")]},
    ],

    "Procurement Compliance Checklist": [
        {"name": "Policy and Vendor Checks",  "icon": "✅", "freq": "100%", "questions": [("procurement_activity", "Procurement activity and applicable policies", "e.g. Cloud SaaS tool procurement — applies to IT Procurement Policy v3.1 and Data Privacy Policy"), ("vendor_checks", "Vendor eligibility and compliance checks completed", "e.g. Vendor security questionnaire completed; GDPR DPA signed; SOC 2 report reviewed")]},
        {"name": "Documentation and Approval","icon":"📋","freq":"100%","questions":[("documentation", "Required documentation verified", "e.g. Signed contract, PO raised, budget approval email, Legal sign-off — all on file in procurement system"), ("final_compliance", "Final compliance confirmation and approver", "e.g. All checks passed; approved by: Sarah Patel, Procurement Director, March 16, 2026")]},
    ],

    # ── Product Management ────────────────────────────────────────────────────

    "Product Requirements Document (PRD)": [
        {"name": "Problem and Objectives",    "icon": "🎯", "freq": "100%", "questions": [("problem_statement", "Problem the product solves", "e.g. Enterprise teams waste 3–5 hours per document on manual writing, formatting, and review cycles"), ("business_objectives", "Business goals this product achieves", "e.g. Increase user activation by 40%; reduce time-to-first-doc to <5 minutes; grow ARR to $5M")]},
        {"name": "Users and Scope",           "icon": "👥", "freq": "100%", "questions": [("target_users", "Primary users and key stakeholders", "e.g. HR Managers (primary), Legal Teams (secondary), IT Admins (admin); CPO, CTO as stakeholders"), ("product_scope", "Features included (and excluded) in this version", "e.g. IN: 90 doc types, section-by-section generation, Notion export. OUT: PDF export, mobile app (v2)")]},
        {"name": "Functional Requirements",   "icon": "⚙️", "freq": "100%", "questions": [("features", "Key features and functional requirements", "e.g. AI-guided Q&A per section; department-filtered doc selection; real-time generation progress"), ("non_functional", "Performance, security, and reliability requirements", "e.g. <5s per section generation; 99.9% uptime; SOC 2 compliant; GDPR data processing")]},
        {"name": "Success Metrics",           "icon": "📊", "freq": "100%", "questions": [("success_metrics", "How product success will be measured", "e.g. Time-to-first-doc <5 min; DAU/MAU >40%; NPS >50; 90-day retention >70%"), ("risks_constraints", "Key risks and constraints", "e.g. LLM rate limits may affect simultaneous users; Groq API dependency; 8-week development timeline")]},
    ],

    "Product Roadmap": [
        {"name": "Vision and Goals",          "icon": "🗺️", "freq": "100%", "questions": [("product_vision", "Product vision and strategic goals", "e.g. Become the default AI document platform for enterprise teams by 2027"), ("key_initiatives", "Key product initiatives for this roadmap", "e.g. H1: Core doc generation; H2: Collaboration features; H3: Advanced analytics and integrations")]},
        {"name": "Milestones and Timeline",   "icon": "📅", "freq": "100%", "questions": [("feature_milestones", "Major features and their planned release dates", "e.g. v2.0 (April): 90 doc types; v2.1 (June): PDF export; v3.0 (Q3): Team collaboration"), ("dependencies", "Dependencies and resource requirements", "e.g. Requires Groq enterprise tier by May; design system v2 needed for collaboration features")]},
    ],

    "Feature Specification": [
        {"name": "Feature Overview",          "icon": "⚙️", "freq": "100%", "questions": [("feature_name", "Feature name and purpose", "e.g. Section-by-Section Generation — generates each document section with a separate LLM call"), ("user_problem", "User problem this feature solves", "e.g. Single-prompt generation produces low-quality later sections; formatting inconsistent across long docs")]},
        {"name": "Requirements and Acceptance","icon":"📋","freq":"100%","questions":[("functional_requirements", "Functional and technical requirements", "e.g. Separate API call per section; context chain from previous sections; streaming progress to UI"), ("acceptance_criteria", "Acceptance criteria for completion", "e.g. All sections generated independently; quality review shows >20% improvement vs single-prompt; tests pass")]},
    ],

    "Release Notes": [
        {"name": "New Features",              "icon": "🆕", "freq": "100%", "questions": [("new_features", "New features introduced in this release", "e.g. Section-by-section generation; 90 document types; live progress indicator during generation"), ("improvements", "Existing feature improvements", "e.g. 40% faster document generation; improved Notion formatting; better section context continuity")]},
        {"name": "Bug Fixes and Notes",       "icon": "🐛", "freq": "100%", "questions": [("bug_fixes", "Bugs fixed in this release", "e.g. Fixed document preview truncation for >3,000 words; fixed Notion publish for docs with tables"), ("known_issues", "Known issues and workaround notes", "e.g. PDF export not yet available (coming v2.1); some older templates may need re-selection")]},
    ],

    "Product Launch Plan": [
        {"name": "Launch Objectives",         "icon": "🚀", "freq": "100%", "questions": [("launch_objectives", "Goals for this product launch", "e.g. 500 signups in first week; 10 press mentions; $50K pipeline generated in first 30 days"), ("target_market", "Target market and audience for launch", "e.g. HR and Legal teams at Series A–C SaaS companies; warm leads from waitlist (1,200 contacts)")]},
        {"name": "Marketing and Timeline",    "icon": "📅", "freq": "100%", "questions": [("marketing_strategy", "Marketing and promotion strategy", "e.g. ProductHunt launch Day 1; email to waitlist; LinkedIn content series; partner co-marketing; press release"), ("launch_timeline", "Launch timeline and key milestones", "e.g. T-7: Embargo brief to press; T-2: Waitlist email; T-0: PH launch + LinkedIn; T+7: Review and optimize")]},
        {"name": "Support and Risk",          "icon": "🛡️", "freq": "100%", "questions": [("support_preparation", "Customer support preparation for launch", "e.g. Launch FAQ published; support team briefed; 24hr coverage for first 3 days; escalation path defined"), ("risk_contingency", "Key launch risks and contingency plans", "e.g. Server load risk → pre-scaled infra, waitlist rollout; negative reviews → response playbook ready")]},
    ],

    "Competitive Analysis Report": [
        {"name": "Competitor Overview",       "icon": "🔍", "freq": "100%", "questions": [("competitors", "Key competitors and their market positioning", "e.g. Ironclad (Legal AI, enterprise, $500K+ ACV); Docusign CLM (contract management); Harvey (law firms)"), ("comparison_scope", "Scope of comparison", "e.g. Comparing features, pricing, target market, AI capabilities, and user experience")]},
        {"name": "Analysis and Insights",     "icon": "📊", "freq": "100%", "questions": [("feature_comparison", "Feature and pricing comparison findings", "e.g. We're 5× cheaper than Ironclad; only solution with section-by-section AI; gap: no mobile app"), ("strategic_insights", "Opportunities for differentiation", "e.g. Mid-market gap — no good solution between $10K and $100K/year; AI-native architecture is key differentiator")]},
    ],

    "Product Strategy Document": [
        {"name": "Vision and Market",         "icon": "🌍", "freq": "100%", "questions": [("vision", "Product vision and strategic objectives", "e.g. Vision: Every enterprise document written by AI by 2028. OKR: 500 customers, $10M ARR by Q4 2026"), ("market_opportunity", "Market opportunity and target segments", "e.g. $15B enterprise document automation market; targeting HR, Legal, Finance at SaaS/tech companies")]},
        {"name": "Strategy and KPIs",         "icon": "🎯", "freq": "100%", "questions": [("strategic_initiatives", "Key strategic initiatives and priorities", "e.g. Expand doc types to 100; launch team collaboration; enterprise SSO; Salesforce integration"), ("kpis", "Success metrics and KPIs", "e.g. ARR, NPS, DAU/MAU, time-to-first-doc, customer retention, expansion revenue")]},
    ],

    "User Persona Document": [
        {"name": "Persona Profile",           "icon": "👤", "freq": "100%", "questions": [("persona_name", "Persona name, role, and demographics", "e.g. 'HR Hannah' — HR Manager, 35 years old, mid-size SaaS company, 5 years HR experience"), ("goals_pains", "Goals, pain points, and needs", "e.g. Goals: Stay compliant, save time on admin. Pains: Manual doc creation takes 3+ hrs; policies constantly outdated")]},
        {"name": "Behaviors and Implications","icon":"🔍","freq":"100%","questions":[("behaviors", "Behavioral characteristics and technology usage", "e.g. Uses Notion, Slack, Workday; mobile-first; prefers templates over blank-slate; values speed over customization"), ("design_implications", "Implications for product design and development", "e.g. Need department-first navigation; doc preview before generating; quick-edit mode; Notion-native export")]},
    ],

    "Product Feedback Report": [
        {"name": "Feedback Summary",          "icon": "📊", "freq": "100%", "questions": [("feedback_sources", "Sources and volume of feedback collected", "e.g. In-app NPS: 320 responses (NPS 58); Support tickets: 85 feedback-related; Customer interviews: 12 sessions"), ("positive_highlights", "Key positive feedback themes", "e.g. Speed of generation praised by 80%; Notion integration loved; section-by-section quality excellent")]},
        {"name": "Issues and Recommendations","icon":"💡","freq":"100%","questions":[("complaints_requests", "Top complaints and feature requests", "e.g. #1: PDF export (requested by 65%); #2: Collaboration/comments; #3: More legal doc types"), ("product_recommendations", "Recommended product improvements", "e.g. PDF export in v2.1 (highest priority); shared workspace in v2.2; expand Legal to 20 types in v2.3")]},
    ],

    "Product Change Request": [
        {"name": "Change Description",        "icon": "🔄", "freq": "100%", "questions": [("change_description", "Description of the requested change", "e.g. Add PDF export functionality — allow downloading generated docs as formatted PDF"), ("reason_impact", "Reason and impact of the change", "e.g. Highest-voted feature request (65% of users); required for enterprise sales; blocks 8 deals in pipeline")]},
        {"name": "Priority and Implementation","icon":"⚙️","freq":"100%","questions":[("priority_feasibility", "Priority level and technical feasibility", "e.g. Priority: P1 — Critical for enterprise sales. Feasibility: Medium — requires WeasyPrint integration, ~3 weeks dev time"), ("implementation_plan", "Implementation and approval workflow", "e.g. Engineering estimate: 3 weeks; Design: 1 week. Approved by CPO; target release: v2.1 (May 2026)")]},
    ],
}


def get_sections_for_doc_type(doc_type: str) -> list:
    """Returns section list for a given doc type. Falls back to generic if not found."""
    sections = _SECTIONS.get(doc_type)
    if sections:
        return sections

    # Generic fallback for any doc type not explicitly defined
    return [
        {"name": "Executive Summary",          "icon": "📋", "freq": "92%",  "questions": [("es_q1", "What is the primary purpose of this document?", "e.g. Define the process for..."), ("es_q2", "Who is the intended audience?", "e.g. All employees / HR department / External clients")]},
        {"name": "Scope and Applicability",    "icon": "🎯", "freq": "88%",  "questions": [("sc_q1", "What areas or people does this document apply to?", "e.g. All full-time staff globally"), ("sc_q2", "What is explicitly excluded from scope?", "e.g. Contractors and freelancers are excluded")]},
        {"name": "Roles and Responsibilities", "icon": "👥", "freq": "85%",  "questions": [("rr_q1", "Who are the key stakeholders and their roles?", "e.g. HR Manager owns policy; Department Heads enforce"), ("rr_q2", "What are the key responsibilities?", "e.g. Manager: approve requests; Employee: submit in system")]},
        {"name": "Key Content",                "icon": "📝", "freq": "100%", "questions": [("pc_q1", "Describe the main content or policy details", "e.g. The process works as follows..."), ("pc_q2", "Are there any special cases or conditions?", "e.g. Exception applies when...")]},
        {"name": "Process and Procedures",     "icon": "⚙️", "freq": "90%",  "questions": [("pp_q1", "What are the step-by-step procedures?", "e.g. Step 1: Submit form; Step 2: Manager review..."), ("pp_q2", "What tools or systems are used?", "e.g. HR system, email approval, Slack notification")]},
        {"name": "Exceptions and Escalation",  "icon": "⚠️", "freq": "80%",  "questions": [("ex_q1", "What exceptions or special circumstances exist?", "e.g. Emergency exceptions approved by C-suite"), ("ex_q2", "How are disputes or edge cases escalated?", "e.g. Escalate to HR Director within 5 business days")]},
        {"name": "Approvals and Sign-off",     "icon": "✅", "freq": "95%",  "questions": [("ap_q1", "Who needs to approve this document?", "e.g. HR Director and Legal Counsel"), ("ap_q2", "What is the review and update cycle?", "e.g. Annual review each January")]},
    ]


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