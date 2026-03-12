"""
DocForge AI — notion_service.py
Fixed Notion schema (updated live):
  - Department: select with exact options: HR, Finance, Legal, Sales, Marketing,
                IT, Operations, Customer Support, Product Management, Procurement
  - Doc Type:   rich_text (free text — no restricted options)
  - Industry:   rich_text (free text)
  - Tags:       REMOVED
  - Status:     select: Draft | Generated | Reviewed | Archived
  - Content stored as plain text (no markdown)
"""
import httpx
import asyncio
from backend.core.config import settings
from backend.core.logger import logger
from backend.schemas.document_schema import NotionPublishRequest, NotionPublishResponse

NOTION_API_URL = "https://api.notion.com/v1"

# Map our department names to the exact Notion select option names
DEPT_MAP = {
    "HR":                  "HR",
    "Human Resources":     "HR",
    "Finance":             "Finance",
    "Finance / Accounting": "Finance",
    "Legal":               "Legal",
    "Sales":               "Sales",
    "Marketing":           "Marketing",
    "IT":                  "IT",
    "Information Technology": "IT",
    "Operations":          "Operations",
    "Customer Support":    "Customer Support",
    "Product Management":  "Product Management",
    "Procurement":         "Procurement",
}


def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }


def chunk_text(text: str, size: int = 1900) -> list[str]:
    """Split plain text into ≤1900-char chunks for Notion paragraph blocks."""
    return [text[i:i+size] for i in range(0, len(text), size)]


def plain_text_to_notion_blocks(plain_text: str) -> list[dict]:
    """
    Convert plain text document to Notion blocks.
    Detects section headings (ALL CAPS line followed by dashes) and paragraph text.
    """
    blocks = []
    lines = plain_text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Detect section heading: uppercase line followed by a dash line
        is_heading = stripped.isupper() and len(stripped) > 3
        next_is_dash = (i + 1 < len(lines)) and bool(lines[i+1].strip().startswith('-') and len(lines[i+1].strip()) > 3)

        if is_heading and next_is_dash:
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": stripped}}],
                    "color": "default"
                }
            })
            i += 2  # skip the dash line too
            continue

        # Detect doc title: very first ALL CAPS line (before meta table)
        if is_heading and i < 3:
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": stripped}}]
                }
            })
            i += 1
            continue

        # Detect meta lines: "Key:    Value"
        if ':' in stripped and not stripped.startswith('-'):
            parts = stripped.split(':', 1)
            if len(parts) == 2 and len(parts[0]) < 30:
                key = parts[0].strip()
                val = parts[1].strip()
                if val:
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": key + ":  "},
                                 "annotations": {"bold": True}},
                                {"type": "text", "text": {"content": val}},
                            ]
                        }
                    })
                    i += 1
                    continue

        # Skip pure dash separator lines
        if all(c == '-' for c in stripped):
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1
            continue

        # Regular paragraph — collect until blank line
        para_lines = []
        while i < len(lines) and lines[i].strip():
            para_lines.append(lines[i].strip())
            i += 1

        para_text = ' '.join(para_lines)
        # Chunk if needed
        for chunk in chunk_text(para_text):
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}]
                }
            })

    return blocks


async def publish_to_notion(request: NotionPublishRequest) -> NotionPublishResponse:
    """Publish plain-text document to Notion database."""
    ctx         = request.company_context or {}
    company     = ctx.get("company_name", "Company")
    industry    = ctx.get("industry", "")
    title       = f"{request.doc_type} — {company}"
    dept        = DEPT_MAP.get(request.department, "Operations")
    word_count  = len(request.gen_doc_full.split())

    logger.info(f"Publishing to Notion: '{title}' | dept={dept} | words={word_count}")

    # Build content blocks from plain text
    blocks = plain_text_to_notion_blocks(request.gen_doc_full)

    # Notion API limits 100 blocks per request — batch if needed
    # For safety, take first 100 blocks (most docs fit)
    blocks = blocks[:100]

    properties = {
        "Title": {
            "title": [{"text": {"content": title}}]
        },
        "Department": {
            "select": {"name": dept}
        },
        "Doc Type": {
            "rich_text": [{"text": {"content": request.doc_type}}]
        },
        "Industry": {
            "rich_text": [{"text": {"content": industry}}]
        },
        "Status": {
            "select": {"name": "Generated"}
        },
        "Created By": {
            "rich_text": [{"text": {"content": "DocForge AI"}}]
        },
        "Version": {"number": 1},
        "Word Count": {"number": word_count},
    }

    payload = {
        "parent": {"database_id": settings.NOTION_DATABASE_ID},
        "properties": properties,
        "children": blocks,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(4):
            resp = await client.post(
                f"{NOTION_API_URL}/pages",
                headers=get_headers(),
                json=payload,
            )
            if resp.status_code == 429:
                wait = 2 ** attempt
                logger.warning(f"Rate limited — waiting {wait}s")
                await asyncio.sleep(wait)
                continue
            break

        if resp.status_code not in (200, 201):
            logger.error(f"Notion error {resp.status_code}: {resp.text}")
            raise Exception(f"Notion API {resp.status_code}: {resp.text[:300]}")

        data       = resp.json()
        notion_url = data.get("url", "")
        page_id    = data.get("id", "")
        logger.info(f"Published: {notion_url}")
        return NotionPublishResponse(notion_url=notion_url, notion_page_id=page_id)


async def fetch_library_from_notion() -> list[dict]:
    """
    Fetch all pages from the Notion database for the library.
    Returns list of {title, doc_type, department, industry, status, notion_url, created_at}
    """
    payload = {
        "sorts": [{"property": "Created At", "direction": "descending"}],
        "page_size": 50,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{NOTION_API_URL}/databases/{settings.NOTION_DATABASE_ID}/query",
            headers=get_headers(),
            json=payload,
        )

    if resp.status_code != 200:
        logger.error(f"Library fetch error: {resp.status_code}")
        return []

    results = resp.json().get("results", [])
    library = []

    for page in results:
        props = page.get("properties", {})

        def get_text(prop_name):
            p = props.get(prop_name, {})
            if p.get("type") == "title":
                items = p.get("title", [])
            elif p.get("type") == "rich_text":
                items = p.get("rich_text", [])
            else:
                return ""
            return "".join(i.get("text", {}).get("content", "") for i in items)

        def get_select(prop_name):
            p = props.get(prop_name, {})
            sel = p.get("select")
            return sel.get("name", "") if sel else ""

        library.append({
            "title":       get_text("Title"),
            "doc_type":    get_text("Doc Type"),
            "department":  get_select("Department"),
            "industry":    get_text("Industry"),
            "status":      get_select("Status"),
            "notion_url":  page.get("url", ""),
            "created_at":  page.get("created_time", "")[:10],
        })

    return library