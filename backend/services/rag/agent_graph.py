"""
<<<<<<< HEAD
agent_graph.py — Agentic CiteRAG using LangGraph StateGraph
=============================================================

Graph topology (3-intent router):

  START
    │
    ▼
  classify_intent
    │
    ├── "create_ticket" ──► handle_create_ticket ──────────────────────────► END
    │
    ├── "update_ticket" ──► handle_update_ticket ──────────────────────────► END
    │
    └── "rag"           ──► classify_confidence ──► (needs_ticket) ──► summarize ──► create_ticket ──┐
                                                └── (skip_ticket) ──────────────────────────────────┴─► update_memory ──► END

Usage (from rag_routes.py):
    from backend.services.rag.agent_graph import run_agent
    result = await run_agent(question, rag_result, session_id)
    # result["intent"] tells you which path was taken
    # result["agent_reply"] is set for create_ticket / update_ticket paths
"""

import logging
import re
from typing import Optional
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END

from backend.services.redis_service import cache

logger = logging.getLogger(__name__)

MEMORY_TTL = 86400
MEMORY_KEY = "docforge:agent:memory:{session_id}"


# ── Typed state ─────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    # Input
    question:        str
    session_id:      str
    rag_result:      dict     # empty dict when intent != "rag"

    # Intent routing
    intent:          str      # "rag" | "create_ticket" | "update_ticket"
    new_status:      str      # extracted status for update_ticket intent

    # RAG sub-path
    confidence:      str
    chunks:          list
    should_ticket:   bool
    ticket_summary:  str
    ticket_id:       Optional[str]

    # Final reply for non-RAG paths
    agent_reply:     str

    # Memory
    memory:          dict


# ── Memory helpers ───────────────────────────────────────────────────────────────

async def _load_memory(session_id: str) -> dict:
=======
agent_graph.py — Tool-Calling Agent with Chat History
======================================================

Architecture:
  - ONE LLM call per user turn using Azure OpenAI Tool Calling
  - LLM sees full chat history → understands context, no Redis state flags needed
  - LLM picks the right tool from: search, create_ticket, select_ticket,
    create_all_tickets, update_ticket, cancel
  - Each tool executes and returns a response
  - Chat history stored in Redis (TTL 24h)

Tools the LLM can call:
  search(question)             → RAG search in documents
  create_ticket()              → Show saved unanswered questions / create ticket
  select_ticket(index)         → Create ticket for specific question from list
  create_all_tickets()         → Create tickets for ALL saved questions
  update_ticket(status)        → Update last ticket status in Notion
  cancel()                     → Cancel current ticket flow
"""

# ── Standard library ──────────────────────────────────────────────────────────
import asyncio
import logging

# ── Third-party ───────────────────────────────────────────────────────────────
import httpx

# ── Internal ──────────────────────────────────────────────────────────────────
from backend.services.redis_service import cache  # Redis client for history + memory

logger = logging.getLogger(__name__)

MEMORY_TTL   = 86400   # 24h
MEMORY_KEY   = "docforge:agent:memory:{session_id}"
HISTORY_KEY  = "docforge:agent:history:{session_id}"
MAX_HISTORY  = 20      # keep last N turns in context


# ── Tool definitions for Azure OpenAI tool calling ────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": (
                "Search turabit's internal documents to answer a question. "
                "Use this whenever the user asks about anything (people, policies, contracts, "
                "clauses, HR, legal, finance, operations, etc.)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The user's question to search for"
                    }
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": (
                "Create a support ticket for unanswered questions. "
                "Use when the user says: 'create ticket', 'raise issue', 'ticket banao', "
                "'open a ticket', 'make a ticket', or similar in any language."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "select_ticket",
            "description": (
                "Select a specific question to create a ticket for when a numbered list "
                "was shown to the user. Use when the user picks by number or ordinal: "
                "'1', 'first', 'second', 'pehla', 'dusra', etc."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "1-based index of the selected question"
                    }
                },
                "required": ["index"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_all_tickets",
            "description": (
                "Create tickets for ALL saved unanswered questions at once. "
                "Use when user says: 'all', 'every', 'both', 'dono', 'sabhi', "
                "'create all', 'all of them', etc."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_ticket",
            "description": (
                "Update the status of a created ticket. "
                "Use when user says: 'mark as resolved', 'close ticket', 'done', 'fixed', "
                "'set to in progress', 'reopen', 'band karo', 'ho gaya', etc. "
                "If user picks from a numbered list (e.g. '1', 'first', 'pehla'), "
                "pass ticket_index=1 (1-based). If no specific ticket mentioned, omit ticket_index."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["Resolved", "In Progress", "Open"],
                        "description": "New status for the ticket"
                    },
                    "ticket_index": {
                        "type": "integer",
                        "description": "1-based index of the ticket to update (if user picked from a list). Omit if only one ticket or unclear."
                    }
                },
                "required": ["status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel",
            "description": (
                "Cancel the current ticket creation flow. "
                "Use when user says: 'cancel', 'no', 'never mind', 'stop', 'chodo', etc."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are CiteRAG, an intelligent assistant for turabit's internal knowledge base.

Your job:
1. Answer questions using turabit's internal documents (HR policies, contracts, legal, finance, operations).
2. When you can't find an answer, save the question and offer to create a support ticket.
3. Manage support ticket creation, selection, and status updates via the provided tools.

RULES:
- ALWAYS call a tool — never reply with plain text directly.
- To answer ANY question (about people, policies, documents, etc.) → call search().
- To create a support ticket → call create_ticket().
- When user picks from a numbered list for CREATION → call select_ticket(index=N).
- When user wants all tickets created → call create_all_tickets().
- When user wants to update a ticket status → call update_ticket(status=...).
  - If user says a number after seeing the update list (e.g. "1", "first", "pehla") → pass ticket_index=N.
  - If user says "all" / "dono" / "sabhi" after seeing the update list → pass ticket_index=-1 (means ALL).
  - If no specific ticket mentioned → omit ticket_index (defaults to 0).
- When user cancels → call cancel().
- You understand all languages (English, Hindi, Gujarati, etc.).\
"""


# ── History helpers ───────────────────────────────────────────────────────────

async def _load_history(session_id: str) -> list:
    """Load chat history from Redis. Returns list of {role, content} dicts."""
    return await cache.get(HISTORY_KEY.format(session_id=session_id)) or []


async def _save_history(session_id: str, history: list):
    """Trim to MAX_HISTORY turns and persist chat history to Redis."""
    trimmed = history[-MAX_HISTORY:]
    await cache.set(HISTORY_KEY.format(session_id=session_id), trimmed, ttl=MEMORY_TTL)



# ── Memory helpers ────────────────────────────────────────────────────────────

async def _load_memory(session_id: str) -> dict:
    """Load agent memory (unanswered questions + created tickets) from Redis."""
>>>>>>> rag
    return await cache.get(MEMORY_KEY.format(session_id=session_id)) or {}


async def _save_memory(session_id: str, memory: dict):
<<<<<<< HEAD
    await cache.set(MEMORY_KEY.format(session_id=session_id), memory, ttl=MEMORY_TTL)


# ── Intent classification (keyword-based, no extra LLM call) ────────────────────

def _classify_intent(question: str) -> str:
    """We removed manual ticket creation. All questions route to RAG."""
    return "rag"



# ── Nodes ────────────────────────────────────────────────────────────────────────

async def node_classify_intent(state: AgentState) -> AgentState:
    """Route the user message: RAG or create ticket."""
    intent = _classify_intent(state["question"])
    logger.info("Intent classified: %s (session=%s)", intent, state["session_id"])
    return {**state, "intent": intent, "new_status": ""}


async def node_handle_create_ticket(state: AgentState) -> AgentState:
    """
    User said 'create ticket'.
    Check Redis memory: was the last RAG answer low-confidence?
      Yes → create ticket in Notion → reply with link
      No  → politely decline
    """
    memory   = await _load_memory(state["session_id"])
    pending  = memory.get("ticket_pending", False)
    last_q   = memory.get("last_question", "")
    last_tid = memory.get("last_ticket_id")

    # Don't create duplicate if one already exists for this turn
    if last_tid and not memory.get("ticket_consumed", False):
        reply = (
            f"🎫 I have already notified the team about this missing information."
        )
        return {**state, "agent_reply": reply}

    if not pending:
        reply = (
            "✅ Your last question was answered well from the documents. "
            "No knowledge gap found — no ticket needed!\n\n"
            "_If you feel the answer was insufficient, ask your question again "
            "and I'll reassess._"
        )
        return {**state, "agent_reply": reply}

    # Ticket is warranted — call create_ticket
    try:
        from backend.services.rag.agent_routes import create_ticket, TicketCreateRequest
        req    = TicketCreateRequest(
            question=last_q or state["question"],
            session_id=state["session_id"],
            attempted_sources=memory.get("last_attempted_sources", []),
            summary=(
                f"User manually requested ticket. "
                f"Original question: \"{(last_q or state['question'])[:200]}\". "
                f"RAG confidence: {memory.get('last_confidence', 'low')}."
            ),
            priority="High" if not memory.get("last_chunks") else "Medium",
            confidence=memory.get("last_confidence", "low"),
        )
        result = await create_ticket(req)
        tid    = result.get("ticket_id", "")
        url    = result.get("url", "")

        # Mark ticket as consumed so we don't duplicate
        memory["last_ticket_id"]      = tid
        memory["last_ticket_url"]     = url
        memory["ticket_pending"]      = False
        memory["ticket_consumed"]     = True
        await _save_memory(state["session_id"], memory)

        reply = (
            f"✅ **Got it!** I've logged this as a knowledge gap and notified the team.\n\n"
            f"_If you want to check or change its status later, just say "
            f"'mark as resolved' or 'set to in progress'._"
        )
    except Exception as exc:
        logger.error("handle_create_ticket failed: %s", exc, exc_info=True)
        reply = "⚠️ Ticket creation failed. Please check the backend logs or Notion permissions."

    return {**state, "agent_reply": reply}


async def node_handle_update_ticket(state: AgentState) -> AgentState:
    """
    User said 'mark as resolved' / 'set to in progress' etc.
    Loads the last ticket_id from Redis and PATCHes Notion.
    """
    memory    = await _load_memory(state["session_id"])
    ticket_id = memory.get("last_ticket_id")
    new_status = state["new_status"]

    if not ticket_id:
        reply = (
            "⚠️ I don't have a ticket on record for this session yet. "
            "Ask a question first, then say 'create ticket' if it couldn't be answered."
        )
        return {**state, "agent_reply": reply}

    try:
        import httpx as _httpx
        from backend.services.rag.agent_routes import _notion_headers, NOTION_API

        headers = _notion_headers()
        body    = {
            "properties": {
                "Status": {"select": {"name": new_status}}
            }
        }
        resp = _httpx.patch(
            f"{NOTION_API}/pages/{ticket_id}",
            headers=headers, json=body, timeout=15,
        )
        resp.raise_for_status()

        # Persist updated status
        memory["last_ticket_status"] = new_status
        await _save_memory(state["session_id"], memory)

        reply = (
            f"✅ **Status updated successfully!**\n\n"
            f"The issue has now been marked as **{new_status}**."
        )
    except Exception as exc:
        logger.error("handle_update_ticket failed: %s", exc, exc_info=True)
        reply = f"⚠️ Could not update ticket status. Error: {exc}"

    return {**state, "agent_reply": reply}


# ── RAG sub-path nodes ───────────────────────────────────────────────────────────

async def node_classify_confidence(state: AgentState) -> AgentState:
    rag    = state["rag_result"]
    conf   = rag.get("confidence", "high")
    chunks = rag.get("chunks", [])
    answer = rag.get("answer", "")
    tool   = rag.get("tool_used", "")

    if tool == "chat":
        should = False
    else:
        total_miss     = (conf == "low") and not chunks
        said_not_found = (conf == "low") and ("could not find" in answer.lower())
        should = total_miss or said_not_found

    return {
        **state,
        "should_ticket": should,
        "confidence":    conf,
        "chunks":        chunks,
        "rag_result": {
            **rag,
            "ticket_pending": should and not rag.get("ticket_id"),
        },
    }


async def node_summarize(state: AgentState) -> AgentState:
    rag       = state["rag_result"]
    citations = rag.get("citations", [])
    chunks    = rag.get("chunks", [])
    question  = state["question"]

    attempted: list[str] = []
    for c in (citations or chunks)[:5]:
        if isinstance(c, dict):
            # Citations use 'text' for the display title, chunks use 'doc_title'
            raw_title = c.get("doc_title") if "doc_title" in c else c.get("text", "")
        else:
            raw_title = str(c)
            
        # Clean for Notion multi-select: max 100 chars, no commas
        clean_title = raw_title.replace(",", "").strip()[:100]
        if clean_title and clean_title not in attempted:
            attempted.append(clean_title)

    summary = (
        f"User asked: \"{question[:200]}\". "
        f"RAG returned {len(chunks)} chunk(s), confidence={state['confidence']}. "
    )
    summary += (
        f"Attempted sources: {', '.join(attempted[:5])}."
        if attempted else
        "No relevant documents found in ChromaDB."
    )
    rag_upd = {**rag, "attempted_sources": attempted}
    return {**state, "ticket_summary": summary, "rag_result": rag_upd}


async def node_auto_create_ticket(state: AgentState) -> AgentState:
    """Auto-create Notion ticket when RAG confidence is too low."""
    try:
        from backend.services.rag.agent_routes import create_ticket, TicketCreateRequest
        
        # Prevent exact duplicate tickets if user spams the same question
        memory = await _load_memory(state["session_id"])
        last_q = memory.get("last_question", "").strip().lower()
        curr_q = state["question"].strip().lower()
        
        if last_q == curr_q and memory.get("last_ticket_id"):
            logger.info("Skipping duplicate auto-ticket for: %s", curr_q)
            ans = state["rag_result"].get("answer", "")
            ans += "\n\n*(Note: Our team is already aware of this missing information and is working on it!)*"
            
            rag_upd = {
                **state["rag_result"],
                "answer": ans,
                "ticket_pending": False,
            }
            return {**state, "rag_result": rag_upd}

        req    = TicketCreateRequest(
            question=state["question"],
            session_id=state["session_id"],
            attempted_sources=state["rag_result"].get("attempted_sources", []),
            summary=state["ticket_summary"],
            priority="High" if not state["chunks"] else "Medium",
            confidence=state["confidence"],
        )
        result = await create_ticket(req)
        tid    = result.get("ticket_id")
        url    = result.get("url")
        logger.info("Auto-ticket created: %s", tid)
        
        ans = state["rag_result"].get("answer", "")
        ans += "\n\n*(Note: A knowledge gap ticket has been automatically created for our team!)*"
        
        rag_upd = {
            **state["rag_result"],
            "answer":         ans,
            "ticket_id":      tid,
            "ticket_url":     url,
            "ticket_pending": False,
        }
        return {**state, "ticket_id": tid, "rag_result": rag_upd}
    except Exception as exc:
        logger.error("node_auto_create_ticket failed: %s", exc, exc_info=True)
        return state


async def node_update_memory(state: AgentState) -> AgentState:
    """Persist session memory to Redis after every turn."""
    try:
        memory = await _load_memory(state["session_id"])
        rag    = state["rag_result"]

        tool_to_intent = {
            "compare":  "compare_docs",
            "analysis": "analyse_docs",
            "refine":   "summarise_doc",
            "full_doc": "full_document",
            "search":   "search",
            "chat":     "greeting",
        }
        tool = rag.get("tool_used", "")
        memory["last_intent"]           = tool_to_intent.get(tool, tool)
        memory["turn_count"]            = memory.get("turn_count", 0) + 1
        memory["last_question"]         = state["question"]
        memory["last_confidence"]       = state["confidence"]
        memory["last_chunks"]           = bool(state["chunks"])
        memory["ticket_pending"]        = rag.get("ticket_pending", False)
        memory["last_attempted_sources"] = rag.get("attempted_sources", [])

        # Track auto-created ticket
        if rag.get("ticket_id"):
            memory["last_ticket_id"]   = rag["ticket_id"]
            memory["last_ticket_url"]  = rag.get("ticket_url", "")
            memory["ticket_consumed"]  = False

        citations = rag.get("citations", [])
        if citations:
            first = citations[0]
            memory["last_doc"] = first.get("text", "") if isinstance(first, dict) else str(first)

        await _save_memory(state["session_id"], memory)
        return {**state, "memory": memory}
    except Exception as exc:
        logger.warning("Memory update failed: %s", exc)
        return state


# ── Conditional edges ────────────────────────────────────────────────────────────

def route_intent(state: AgentState) -> str:
    return state["intent"]   # "rag" | "create_ticket" | "update_ticket"


def route_confidence(state: AgentState) -> str:
    return "needs_ticket" if state["should_ticket"] else "skip_ticket"


# ── Build and compile the graph ──────────────────────────────────────────────────

def _build_graph():
    g = StateGraph(AgentState)

    # Register all nodes
    g.add_node("classify_intent",      node_classify_intent)
    g.add_node("classify_confidence",  node_classify_confidence)
    g.add_node("summarize",            node_summarize)
    g.add_node("auto_create_ticket",   node_auto_create_ticket)
    g.add_node("update_memory",        node_update_memory)

    # Entry
    g.set_entry_point("classify_intent")

    # Top-level intent routing
    g.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "rag": "classify_confidence",
        },
    )

    # RAG path: confidence routing
    g.add_conditional_edges(
        "classify_confidence",
        route_confidence,
        {
            "needs_ticket": "summarize",
            "skip_ticket":  "update_memory",
        },
    )
    g.add_edge("summarize",          "auto_create_ticket")
    g.add_edge("auto_create_ticket", "update_memory")
    g.add_edge("update_memory",      END)

    return g.compile()


_graph = _build_graph()
logger.info("LangGraph agent compiled — nodes: %s", list(_graph.nodes.keys()))


# ── Public interface ─────────────────────────────────────────────────────────────
=======
    """Persist agent memory dict to Redis with 24-hour TTL."""
    await cache.set(MEMORY_KEY.format(session_id=session_id), memory, ttl=MEMORY_TTL)


# ── Priority detection ────────────────────────────────────────────────────────

_HIGH_SIGNALS = [
    "password", "login", "access denied", "blocked", "unauthorized",
    "security", "breach", "data leak", "hacked", "legal", "lawsuit",
    "compliance", "gdpr", "audit", "contract", "nda", "termination",
    "salary", "payment", "payroll", "invoice", "not paid", "overdue",
    "urgent", "asap", "critical", "emergency", "broken", "down", "outage",
]


def _detect_priority(question: str) -> str:
    """Return 'High' if the question contains any urgency/security/finance signal words, else 'Low'."""
    q = question.lower()
    if any(s in q for s in _HIGH_SIGNALS):
        return "High"
    return "Low"


# ── Tool executors ────────────────────────────────────────────────────────────

async def _tool_search(question: str, session_id: str, rag_result: dict) -> str:
    """Return the RAG answer (already computed by rag_routes before calling run_agent)."""
    conf   = rag_result.get("confidence", "high")
    answer = rag_result.get("answer", "")
    tool   = rag_result.get("tool_used", "search")

    not_found = conf == "low" or "could not find" in answer.lower()

    if not_found:
        memory    = await _load_memory(session_id)
        unanswered = memory.get("unanswered_questions", [])
        existing  = {u["question"].lower().strip() for u in unanswered}

        unanswered_new = rag_result.get("_unanswered_questions", [])
        if not unanswered_new:
            unanswered_new = [{"question": question, "raw_chunks": []}]

        for item in unanswered_new:
            if item["question"].lower().strip() not in existing:
                unanswered.append(item)
                existing.add(item["question"].lower().strip())

        memory["unanswered_questions"] = unanswered
        await _save_memory(session_id, memory)
        logger.info("📋 Unanswered saved — total: %d", len(unanswered))
        return answer or "I could not find information about this in the available documents."

    return answer


async def _tool_create_ticket(session_id: str) -> str:
    """Show list of unanswered questions and ask which one, or create directly if 1."""
    memory     = await _load_memory(session_id)
    unanswered = memory.get("unanswered_questions", [])

    if not unanswered:
        return (
            "ℹ️ No unanswered questions saved yet.\n\n"
            "Ask me something — if I can't find it, I'll save it "
            "and you can say **create ticket** anytime."
        )

    if len(unanswered) == 1:
        reply, _ = await _make_ticket(unanswered[0]["question"], session_id, memory)
        memory["unanswered_questions"] = []   # clear after creating
        await _save_memory(session_id, memory)  # BUG FIX: must save here
        return reply

    lines = "\n".join(f"  {i+1}. {u['question']}" for i, u in enumerate(unanswered))
    return (
        f"I have **{len(unanswered)}** unanswered questions saved:\n\n"
        f"{lines}\n\n"
        f"Which would you like a ticket for? Say a **number**, **'all'**, or **'cancel'**."
    )


async def _tool_select_ticket(index: int, session_id: str) -> str:
    """Create a ticket for the question at 1-based index."""
    memory     = await _load_memory(session_id)
    unanswered = memory.get("unanswered_questions", [])

    if not unanswered:
        return "ℹ️ No pending questions — feel free to ask anything!"

    idx = index - 1
    if not (0 <= idx < len(unanswered)):
        lines = "\n".join(f"  {i+1}. {u['question']}" for i, u in enumerate(unanswered))
        return f"Please pick a number between 1 and {len(unanswered)}:\n\n{lines}"

    reply, _ = await _make_ticket(unanswered[idx]["question"], session_id, memory)
    memory["unanswered_questions"] = [u for i, u in enumerate(unanswered) if i != idx]
    await _save_memory(session_id, memory)
    return reply


async def _tool_create_all_tickets(session_id: str) -> str:
    """
    Create tickets for ALL saved unanswered questions — runs in background.

    Returns an instant reply to the user (< 0.1s) and fires off ticket
    creation as a background task so the response is never delayed.
    Tickets are created sequentially (to avoid Notion rate limits) but
    non-blocking — the user can continue chatting immediately.
    """
    memory     = await _load_memory(session_id)
    unanswered = memory.get("unanswered_questions", [])

    if not unanswered:
        return "ℹ️ No pending questions to create tickets for."

    questions = [item["question"] for item in unanswered]
    count     = len(questions)

    # ── Background job ────────────────────────────────────────────────────────
    async def _create_all_in_background():
        """Create tickets sequentially in background after instant reply is sent."""
        bg_memory = await _load_memory(session_id)
        created   = 0
        failed    = 0

        for q in questions:
            try:
                _line, _ = await _make_ticket(q, session_id, bg_memory)
                bg_memory = await _load_memory(session_id)  # refresh after each create
                created += 1
                logger.info("🎫 [BG] ticket %d/%d done session=%s", created, count, session_id)
            except Exception as e:
                failed += 1
                logger.error("🔴 [BG] ticket failed q='%s': %s", q[:60], e)

        # ── Clear queue + write completion status ──────────────────────────────
        bg_memory["unanswered_questions"] = []
        bg_memory["batch_create_status"] = {
            "total":   count,
            "created": created,
            "failed":  failed,
            "done":    True,
        }
        await _save_memory(session_id, bg_memory)
        logger.info("✅ [BG] batch done: %d created %d failed session=%s", created, failed, session_id)

    # Fire and forget — user gets reply instantly, tickets create in background
    asyncio.create_task(_create_all_in_background())

    # ── Instant reply to user ─────────────────────────────────────────────────
    q_list = "\n".join(f"  {i+1}. {q}" for i, q in enumerate(questions))
    return (
        f"⏳ Creating **{count} ticket{'s' if count > 1 else ''}** in the background:\n\n"
        f"{q_list}\n\n"
        "You can keep chatting — check **My Tickets** in Notion in a moment to see them appear. ✅"
    )



async def _tool_update_ticket(status: str, session_id: str, ticket_index: int = 0) -> str:
    """
    Update a ticket's status in Notion.

    Logic:
      - No tickets → helpful message
      - 1 ticket   → update it directly
      - 2+ tickets, no index → show numbered list and ask which one
      - 2+ tickets, index given → update that specific ticket
      - ticket_index == -1  → update ALL tickets (user said 'all')
    """
    import httpx as _httpx
    from backend.services.rag.agent_routes import _notion_headers, NOTION_API

    memory  = await _load_memory(session_id)
    tickets = memory.get("created_tickets", [])

    # ── Fallback: legacy memory that only has last_page_id ────────────────────
    if not tickets and memory.get("last_page_id"):
        tickets = [{
            "ticket_id": memory.get("last_ticket_id", "?"),
            "page_id":   memory["last_page_id"],
            "question":  "(previous ticket)",
            "status":    memory.get("last_ticket_status", "Open"),
        }]

    if not tickets:
        return (
            "⚠️ No ticket on record for this session. "
            "Ask something, say **create ticket**, then you can update its status."
        )

    # ── Multiple tickets — no index → show selection list ─────────────────────
    if len(tickets) > 1 and ticket_index == 0:
        lines = "\n".join(
            f"  {i+1}. **{t['question']}** — `{t['ticket_id']}` ({t.get('status','Open')})"
            for i, t in enumerate(tickets)
        )
        return (
            f"You have **{len(tickets)}** tickets. Which one should be marked **{status}**?\n\n"
            f"{lines}\n\n"
            f"Say a **number** or **'all'** to update all."
        )

    # ── Resolve target(s) ─────────────────────────────────────────────────────
    if ticket_index == -1:          # -1 = sentinel for "all"
        targets = tickets
    elif ticket_index == 0:
        targets = tickets           # only 1 ticket
    else:
        idx = ticket_index - 1
        if not (0 <= idx < len(tickets)):
            lines = "\n".join(
                f"  {i+1}. {t['question']}" for i, t in enumerate(tickets)
            )
            return f"Please pick a number between 1 and {len(tickets)}:\n\n{lines}"
        targets = [tickets[idx]]

    # ── Perform async Notion PATCH for each target ────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            results = []
            for t in targets:
                resp = await client.patch(
                    f"{NOTION_API}/pages/{t['page_id']}",
                    headers=_notion_headers(),
                    json={"properties": {"Status": {"select": {"name": status}}}},
                )
                resp.raise_for_status()
                t["status"] = status
                results.append(f"✅ `{t['ticket_id']}` → **{status}** ({t['question']})")

        memory["created_tickets"]    = tickets
        memory["last_ticket_status"] = status
        await _save_memory(session_id, memory)
        return "\n".join(results)

    except Exception as e:
        logger.error("update_ticket failed: %s", e)
        return f"⚠️ Could not update ticket status. Error: {e}"


async def _tool_cancel(session_id: str) -> str:
    """Cancel current ticket flow — nothing is deleted."""
    memory = await _load_memory(session_id)
    count  = len(memory.get("unanswered_questions", []))
    # We keep unanswered_questions — user can say create ticket later
    await _save_memory(session_id, memory)
    if count:
        return (
            f"👍 Cancelled. You still have **{count}** saved question(s) — "
            f"say **create ticket** anytime to continue."
        )
    return "👍 Cancelled."


# ── Core ticket creation ──────────────────────────────────────────────────────

async def _make_ticket(question: str, session_id: str, memory: dict) -> tuple[str, str]:
    """Dedup check → create Notion ticket. Updates memory in-place."""
    from backend.services.rag.ticket_dedup import find_duplicate
    from backend.services.rag.agent_routes import _create_notion_ticket, TicketCreateRequest

    dup = await find_duplicate(question)
    if dup:
        tid = dup["ticket_id"]
        logger.info("🚫 Dedup blocked ticket=%s q='%s'", tid, question[:50])
        return f"🎫 Ticket already exists for: **{question}**", tid

    priority = _detect_priority(question)
    req = TicketCreateRequest(
        question=question,
        session_id=session_id,
        attempted_sources=[],
        summary=f"RAG could not answer: \"{question[:200]}\"",
        priority=priority,
        confidence="low",
    )
    result  = await _create_notion_ticket(req)
    tid     = result.get("ticket_id", "")
    page_id = result.get("page_id", "")
    url     = result.get("url", "")

    memory["last_ticket_id"]  = tid
    memory["last_page_id"]    = page_id
    memory["last_ticket_url"] = url

    # ── Track ALL created tickets (for multi-ticket status update) ────────────
    created = memory.get("created_tickets", [])
    created.append({
        "ticket_id": tid,
        "page_id":   page_id,
        "url":       url,
        "question":  question,
        "status":    "Open",
    })
    memory["created_tickets"] = created

    logger.info("🎫 Ticket created id=%s priority=%s q='%s'", tid, priority, question[:50])
    return f"✅ Ticket created for: **{question}**", tid


# ── Main agent entry point ────────────────────────────────────────────────────
>>>>>>> rag

async def run_agent(
    question:   str,
    rag_result: dict,
    session_id: str = "default",
) -> dict:
    """
<<<<<<< HEAD
    Run the agentic LangGraph graph over a user message.

    For RAG questions: enriches rag_result with ticket_pending / ticket_id / ticket_url.
    For ticket commands: returns rag_result with agent_reply set and intent set.

    The caller (rag_routes.py) checks result["intent"] to decide the response.
    """
    initial: AgentState = {
        "question":        question,
        "session_id":      session_id,
        "rag_result":      rag_result,
        "intent":          "rag",
        "new_status":      "",
        "confidence":      rag_result.get("confidence", "high"),
        "chunks":          rag_result.get("chunks", []),
        "should_ticket":   False,
        "ticket_summary":  "",
        "ticket_id":       None,
        "agent_reply":     "",
        "memory":          {},
    }

    try:
        final = await _graph.ainvoke(initial)
        result = dict(final["rag_result"])
        result["intent"]      = final["intent"]
        result["agent_reply"] = final.get("agent_reply", "")
        return result
    except Exception as exc:
        logger.error("LangGraph agent error: %s", exc, exc_info=True)
        rag_result["intent"]      = "rag"
        rag_result["agent_reply"] = ""
        return rag_result
=======
    Run the tool-calling agent.

    Flow:
      1. Build messages = [system] + chat_history + [user]
      2. Call LLM with tools → LLM picks a tool
      3. Execute the tool
      4. Save history (user + assistant reply)
      5. Return enriched result dict
    """
    from backend.services.rag.rag_service import _get_llm

    # ── 1. Build message list ─────────────────────────────────────────────────
    history  = await _load_history(session_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    # ── 2. LLM tool-call ──────────────────────────────────────────────────────
    try:
        llm = _get_llm()
        llm_with_tools = llm.bind_tools(TOOLS)

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: llm_with_tools.invoke(messages)
        )

        tool_calls = getattr(response, "tool_calls", []) or []

        if not tool_calls:
            # LLM replied without calling a tool (shouldn't happen with good prompt)
            # Fall back to search
            logger.warning("LLM returned no tool call — defaulting to search")
            tool_calls = [{"name": "search", "args": {"question": question}}]

        tool_call  = tool_calls[0]
        tool_name  = tool_call["name"]
        tool_args  = tool_call.get("args", {})

        logger.info("🔧 Tool called: %s args=%s", tool_name, tool_args)

    except Exception as e:
        logger.error("LLM tool-call failed: %s — falling back to search result", e)
        tool_name = "search"
        tool_args = {"question": question}

    # Guarantee tool_name is always set (defensive, should never be needed)
    if "tool_name" not in locals():
        tool_name = "search"
        tool_args = {"question": question}

    # ── 3. Execute tool ───────────────────────────────────────────────────────
    try:
        if tool_name == "search":
            reply = await _tool_search(
                question=tool_args.get("question", question),
                session_id=session_id,
                rag_result=rag_result,
            )
        elif tool_name == "create_ticket":
            reply = await _tool_create_ticket(session_id)
        elif tool_name == "select_ticket":
            reply = await _tool_select_ticket(
                index=int(tool_args.get("index", 1)),
                session_id=session_id,
            )
        elif tool_name == "create_all_tickets":
            reply = await _tool_create_all_tickets(session_id)
        elif tool_name == "update_ticket":
            reply = await _tool_update_ticket(
                status=tool_args.get("status", "Resolved"),
                session_id=session_id,
                ticket_index=int(tool_args.get("ticket_index", 0)),
            )
        elif tool_name == "cancel":
            reply = await _tool_cancel(session_id)
        else:
            logger.warning("Unknown tool: %s", tool_name)
            reply = await _tool_search(question, session_id, rag_result)

    except Exception as e:
        logger.error("Tool execution failed (%s): %s", tool_name, e, exc_info=True)
        reply = rag_result.get("answer", "Something went wrong. Please try again.")

    # ── 4. Save to chat history (single atomic write) ─────────────────────────
    history = await _load_history(session_id)
    history.append({"role": "user",      "content": question})
    history.append({"role": "assistant", "content": reply})
    await _save_history(session_id, history)

    # ── 5. Return result ──────────────────────────────────────────────────────
    result = dict(rag_result)
    result["tool_used"] = tool_name
    result["intent"]    = tool_name
    if tool_name == "search":
        # answer shown as main message — agent_reply empty so blue box never appears
        result["answer"]      = reply
        result["agent_reply"] = ""
        result["confidence"]  = rag_result.get("confidence", "high")
    else:
        # ticket / status action — blue box IS the message
        result["answer"]      = reply
        result["agent_reply"] = reply
        result["confidence"]  = "high"
        result["citations"]   = []
        result["chunks"]      = []

    return result
>>>>>>> rag
