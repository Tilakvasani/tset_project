from typing import List, Tuple
from mcp.types import Prompt, PromptMessage
from core.chat import Chat
from core.claude import Claude
from mcp_client import MCPClient

SYSTEM_PROMPT = """You are a powerful HubSpot CRM agent with full access to HubSpot through 8 universal tools.

## YOUR 8 TOOLS

### 1. crm_object_action — ALL CRM objects
One tool for every CRM object. Use action: search | get | list | create | update | delete | associate | merge
Objects: contacts, companies, deals, tickets, leads, quotes, invoices, orders, products,
         line_items, subscriptions, goals, appointments, marketing_events, services, courses, carts

### 2. engagement_action — All activity types
One tool for notes, calls, emails, meetings, tasks.
Use action: create | update | list | get_timeline

### 3. automation_action — Workflows + Sequences
List workflows, enroll/unenroll contacts. type: workflow | sequence

### 4. marketing_action — Campaigns, Lists, Forms
type: campaign | list | form. action: list | get | create | add_contacts | submissions

### 5. conversation_action — Inbox + Communication Preferences
type: thread | preferences. action: list | get | send | archive | update

### 6. analytics_action — Reports, Events, GraphQL, Forecasts
type: report | event | graphql | forecast. action: query | send_event | list_defs | get

### 7. cms_action — Knowledge Base, Domains, Files
type: knowledge_base | domain | file. action: list | get | create | update | publish | archive

### 8. settings_action — Users, Teams, Owners, Properties, Pipelines
type: user | team | owner | property | pipeline | currency. action: list | get | create

## CONTEXT RESOURCES (auto-injected, never guess IDs)
- hubspot://pipelines          → deal pipeline stage IDs
- hubspot://ticket-pipelines   → ticket pipeline stage IDs
- hubspot://owners             → owner IDs and emails
- hubspot://contact-properties → valid contact property names
- hubspot://deal-properties    → valid deal property names

## SLASH COMMANDS
/find_contact <email or name>
/deal_report [stage]
/create_contact_flow <email>
/contact_summary <contact_id>
/pipeline_overview
/log_call_flow <name or email>
/ticket_triage [priority]

## RULES
1. ALWAYS check hubspot://pipelines or hubspot://owners resource before using IDs — never guess.
2. ALWAYS confirm with user before create, update, or delete actions.
3. Present CRM data in clean formatted tables or summaries with emojis.
4. If a tool returns an error, explain it clearly and suggest how to fix it.
5. When associating records, always do it right after creating the record.
6. For timeline/history requests always use engagement_action with get_timeline.
7. Never expose the HUBSPOT_TOKEN or any credentials.
8. Reference documents with @filename syntax.
"""


class CliChat(Chat):
    def __init__(self, doc_client: MCPClient, clients: dict[str, MCPClient], claude_service: Claude):
        super().__init__(clients=clients, claude_service=claude_service)
        self.doc_client = doc_client

    async def list_prompts(self) -> list[Prompt]:
        all_prompts = []
        for client in self.clients.values():
            try:
                all_prompts.extend(await client.list_prompts())
            except Exception:
                pass
        return all_prompts

    async def list_docs_ids(self) -> list[str]:
        try:
            return await self.doc_client.read_resource("docs://documents")
        except Exception:
            return []

    async def get_doc_content(self, doc_id: str) -> str:
        try:
            return await self.doc_client.read_resource(f"docs://documents/{doc_id}")
        except Exception:
            return ""

    async def get_prompt(self, command: str, arg: str) -> list[PromptMessage]:
        arg_variants = [
            {"identifier": arg},
            {"contact_id": arg},
            {"email": arg},
            {"doc_id": arg},
            {"stage_filter": arg},
            {"contact_identifier": arg},
            {"priority": arg},
        ]
        for client in self.clients.values():
            for kwargs in arg_variants:
                try:
                    result = await client.get_prompt(command, kwargs)
                    if result:
                        return result
                except Exception:
                    continue
        return []

    async def _extract_resources(self, query: str) -> str:
        mentions = [w[1:] for w in query.split() if w.startswith("@")]
        doc_ids = await self.list_docs_ids()
        mentioned = [(d, await self.get_doc_content(d)) for d in doc_ids if d in mentions]
        return "".join(f'\n<document id="{d}">\n{c}\n</document>\n' for d, c in mentioned)

    async def _process_command(self, query: str) -> bool:
        if not query.startswith("/"):
            return False
        words = query.split()
        command = words[0].lstrip("/")
        arg = words[1] if len(words) > 1 else ""
        messages = await self.get_prompt(command, arg)
        if messages:
            self.messages += convert_prompt_messages_to_message_params(messages)
            return True
        return False

    async def _process_query(self, query: str):
        if await self._process_command(query):
            return
        resources = await self._extract_resources(query)
        prompt = f"""User request:
<query>{query}</query>
{f"<context>{resources}</context>" if resources else ""}
Use your HubSpot tools to fulfill this request. Be direct and helpful."""
        self.messages.append({"role": "user", "content": prompt})


def convert_prompt_message_to_message_param(pm: PromptMessage) -> dict:
    role = "user" if pm.role == "user" else "assistant"
    content = pm.content
    ctype = content.get("type") if isinstance(content, dict) else getattr(content, "type", None)
    if ctype == "text":
        text = content.get("text", "") if isinstance(content, dict) else getattr(content, "text", "")
        return {"role": role, "content": text}
    if isinstance(content, list):
        parts = []
        for item in content:
            t = item.get("type") if isinstance(item, dict) else getattr(item, "type", None)
            if t == "text":
                parts.append(item.get("text", "") if isinstance(item, dict) else getattr(item, "text", ""))
        if parts:
            return {"role": role, "content": "\n".join(parts)}
    return {"role": role, "content": ""}


def convert_prompt_messages_to_message_params(messages: List[PromptMessage]) -> List[dict]:
    return [convert_prompt_message_to_message_param(m) for m in messages]
