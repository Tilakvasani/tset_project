import asyncio
import httpx
from backend.core.config import settings
from backend.core.logger import logger
from backend.schemas.notion_schema import NotionPublishRequest

NOTION_API_URL = "https://api.notion.com/v1"

def get_headers():
    return {
        "Authorization": f"Bearer {settings.NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

def chunk_content(content: str, chunk_size: int = 1900) -> list:
    return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

def parse_version(version: str) -> float:
    try:
        return float(str(version).lower().replace("v", "").strip().split(".")[0])
    except:
        return 1.0

async def with_backoff_async(fn, retries: int = 5):
    for attempt in range(retries):
        try:
            return await fn()
        except Exception as e:
            if "rate_limited" in str(e).lower() or "429" in str(e):
                wait = 2 ** attempt
                logger.warning(f"Rate limited. Waiting {wait}s before retry {attempt+1}")
                await asyncio.sleep(wait)
            else:
                raise e
    raise Exception("Max retries exceeded for Notion API")

async def publish_to_notion(request: NotionPublishRequest) -> str:
    """Publish document to Notion database"""
    logger.info(f"Publishing to Notion: {request.title}")

    chunks = chunk_content(request.content)
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
            "Title": {"title": [{"text": {"content": request.title}}]},
            "Industry": {"select": {"name": request.industry}},
            "Doc Type": {"select": {"name": request.doc_type}},
            "Version": {"number": parse_version(request.version)},
            "Created By": {"rich_text": [{"text": {"content": request.created_by}}]},
            "Tags": {"multi_select": [{"name": tag} for tag in request.tags]},
            "Status": {"select": {"name": "Generated"}},
            "Word Count": {"number": len(request.content.split())},
            "Source Template ID": {"rich_text": [{"text": {"content": request.template_id or ""}}]}
        },
        "children": blocks
    }

    async with httpx.AsyncClient() as client:
        async def do_request():
            response = await client.post(
                f"{NOTION_API_URL}/pages",
                headers=get_headers(),
                json=payload,
                timeout=30
            )
            if response.status_code == 429:
                raise Exception("rate_limited")
            if response.status_code != 200:
                raise Exception(f"Notion API error: {response.text}")
            return response

        response = await with_backoff_async(do_request)
        data = response.json()
        notion_url = data.get("url", "")
        logger.info(f"Published to Notion: {notion_url}")
        return notion_url


async def get_documents_from_notion() -> list:
    """Fetch all documents from Notion database"""
    logger.info("Fetching documents from Notion")

    payload = {
        "page_size": 100,
        "sorts": [{"timestamp": "created_time", "direction": "descending"}]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NOTION_API_URL}/databases/{settings.NOTION_DATABASE_ID}/query",
            headers=get_headers(),
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Notion API error: {response.text}")

        data = response.json()
        results = data.get("results", [])

        docs = []
        for page in results:
            props = page.get("properties", {})

            def get_title(p):
                items = p.get("title", [])
                return items[0]["text"]["content"] if items else ""

            def get_select(p):
                s = p.get("select")
                return s["name"] if s else ""

            def get_text(p):
                items = p.get("rich_text", [])
                return items[0]["text"]["content"] if items else ""

            def get_multi_select(p):
                return [s["name"] for s in p.get("multi_select", [])]

            def get_number(p):
                return p.get("number", 0) or 0

            docs.append({
                "doc_id": page.get("id", ""),
                "title": get_title(props.get("Title", {})),
                "doc_type": get_select(props.get("Doc Type", {})),
                "industry": get_select(props.get("Industry", {})),
                "version": str(int(get_number(props.get("Version", {})) or 1)),
                "tags": get_multi_select(props.get("Tags", {})),
                "created_by": get_text(props.get("Created By", {})),
                "status": get_select(props.get("Status", {})),
                "word_count": get_number(props.get("Word Count", {})),
                "notion_url": page.get("url", ""),
                "created_at": page.get("created_time", ""),
                "published": True,
                "content": "Document stored in Notion. Click 'View in Notion' to read full content."
            })

        return docs
