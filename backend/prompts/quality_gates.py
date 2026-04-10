from typing import Tuple

# H1 FIX: Map full display names → slug keys so the quality gate fires correctly.
# routes.py passes the raw doc_type string from the request; this normalises it.
DOC_TYPE_NORMALISE: dict[str, str] = {
    # exact display names used in the UI / database
    "standard operating procedure": "sop",
    "sop":                          "sop",
    "policy":                       "policy",
    "hr policy":                    "policy",
    "proposal":                     "proposal",
    "business proposal":            "proposal",
    "statement of work":            "sow",
    "sow":                          "sow",
    "incident report":              "incident_report",
    "faq":                          "faq",
    "frequently asked questions":   "faq",
    "business case":                "business_case",
    "security policy":              "security_policy",
    "kpi report":                   "kpi_report",
    "runbook":                      "runbook",
    "run book":                     "runbook",
}

REQUIRED_SECTIONS = {
    "sop":             ["purpose", "scope", "procedure", "responsibilities"],
    "policy":          ["purpose", "scope", "definitions", "exceptions"],
    "proposal":        ["overview", "objectives", "timeline", "budget"],
    "sow":             ["scope", "deliverables", "timeline", "payment"],
    "incident_report": ["summary", "impact", "root cause", "resolution"],
    "faq":             ["question", "answer"],
    "business_case":   ["problem", "solution", "benefits", "cost"],
    "security_policy": ["scope", "definitions", "requirements", "exceptions"],
    "kpi_report":      ["overview", "metrics", "analysis", "recommendations"],
    "runbook":         ["purpose", "prerequisites", "steps", "troubleshooting"],
}

MIN_WORD_COUNT = 150


def normalise_doc_type(doc_type: str) -> str:
    """Convert a display name or slug to the canonical REQUIRED_SECTIONS key."""
    return DOC_TYPE_NORMALISE.get(doc_type.lower().strip(), doc_type.lower().strip())


def check_quality(content: str, doc_type: str) -> Tuple[bool, str]:
    """Check if generated document meets quality standards."""
    content_lower = content.lower()

    word_count = len(content.split())
    if word_count < MIN_WORD_COUNT:
        return False, f"Too short: {word_count} words (minimum {MIN_WORD_COUNT})"

    # H1 FIX: normalise doc_type before lookup so "Standard Operating Procedure" → "sop"
    slug = normalise_doc_type(doc_type)
    required = REQUIRED_SECTIONS.get(slug, [])
    missing = [s for s in required if s not in content_lower]

    if missing:
        return False, f"Missing required sections: {', '.join(missing)}"

    return True, "Quality check passed"