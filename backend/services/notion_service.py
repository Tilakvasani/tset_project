"""
DocForge AI — notion_service.py
Updated to work with the new gen_doc workflow.
Publishes the final assembled document to Notion.
"""
import time
import httpx
from backend.core.config import settings
from backend.core.logger import logger
from backend.schemas.document_schema import NotionPublishRequest, NotionPublishResponse

NOTION_API_URL = "https://api.notion.com/v1"


def get_headers():
    return {
        "Authorization": f"Bearer {settings.NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }


def chunk_content(content: str, chunk_size: int = 1900) -> list:
    """Split content into Notion-safe chunks (max 2000 chars per block)."""
    return [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]


def with_backoff(fn, retries: int = 5):
    """Exponential backoff for Notion rate limits."""
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            if "rate_limited" in str(e).lower() or "429" in str(e):
                wait = 2 ** attempt
                logger.warning(f"Rate limited. Waiting {wait}s before retry {attempt + 1}")
                time.sleep(wait)
            else:
                raise e
    raise Exception("Max retries exceeded for Notion API")


async def publish_to_notion(request: NotionPublishRequest) -> NotionPublishResponse:
    """
    Publish the final generated document to Notion.
    Takes gen_doc_full (markdown text) and publishes it as a new Notion page.
    """
    logger.info(f"Publishing to Notion: gen_id={request.gen_id}, doc_type={request.doc_type}")

    ctx = request.company_context or {}
    title = f"{request.doc_type} — {ctx.get('company_name', 'Company')}"
    chunks = chunk_content(request.gen_doc_full)

    # Build content blocks
    blocks = []
    for chunk in chunks:
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            }
        })

    payload = {
        "parent": {"database_id": settings.NOTION_DATABASE_ID},
        "properties": {
            "Title": {
                "title": [{"text": {"content": title}}]
            },
            "Department": {
                "select": {"name": request.department}
            },
            "Doc Type": {
                "select": {"name": request.doc_type}
            },
            "Version": {
                "rich_text": [{"text": {"content": "v1.0"}}]
            },
            "Created By": {
                "rich_text": [{"text": {"content": "DocForge AI"}}]
            }
        },
        "children": blocks
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NOTION_API_URL}/pages",
            headers=get_headers(),
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            notion_url = data.get("url", "")
            notion_page_id = data.get("id", "")
            logger.info(f"Published to Notion: {notion_url}")
            return NotionPublishResponse(
                notion_url=notion_url,
                notion_page_id=notion_page_id
            )
        else:
            raise Exception(f"Notion API error: {response.text}")