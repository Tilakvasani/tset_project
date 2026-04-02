"""
shared.py — Shared imports, CSS, API helpers, and session initialiser
for DocForge AI / CiteRAG.  Every tab module imports from here.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import httpx

try:
    from docx_builder import build_docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/") + "/api"


st.set_page_config(
    page_title="DocForge AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Global font ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0f111a;
    border-right: 1px solid #1e2433;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stRadio label { font-size: 0.85rem; }

/* ── Main background ── */
.main .block-container { background: #0d0f18; padding-top: 2rem; margin-top: 0.75rem; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: #131722;
    border: 1px solid #1e2843;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
}
[data-testid="stChatMessage"][data-testid*="user"] {
    background: #1a1f35;
    border-color: #2a3a6e;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: #131722 !important;
    border: 1px solid #2a3a6e !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}

/* ── Tables in chat (comparison) ── */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.75rem 0;
    font-size: 0.85rem;
}
th {
    background: #1e2843;
    color: #93c5fd;
    padding: 8px 12px;
    text-align: left;
    border: 1px solid #2a3a6e;
    font-weight: 600;
}
td {
    padding: 7px 12px;
    border: 1px solid #1e2433;
    color: #cbd5e1;
}
tr:nth-child(even) td { background: #131722; }
tr:nth-child(odd) td { background: #0f111a; }
tr:hover td { background: #1a2035; }

/* ── Dividers ── */
hr { border-color: #1e2433 !important; margin: 0.5rem 0 !important; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 500;
    transition: all 0.15s;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    border: none !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="secondary"] {
    background: #131722 !important;
    border: 1px solid #1e2843 !important;
    color: #94a3b8 !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #3b82f6 !important;
    color: #93c5fd !important;
}

/* ── Info/warning boxes ── */
[data-testid="stInfo"] {
    background: #0c1a2e !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    color: #93c5fd !important;
}
[data-testid="stWarning"] {
    background: #1c1200 !important;
    border: 1px solid #3d2a00 !important;
    border-radius: 8px !important;
    color: #fcd34d !important;
}

/* ── Caption text ── */
.stCaption { color: #475569 !important; font-size: 0.75rem !important; }

/* ── Confidence badge ── */
.cite-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.cite-high   { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.cite-medium { background: #1c1a00; color: #facc15; border: 1px solid #854d0e; }
.cite-low    { background: #1c0a0a; color: #f87171; border: 1px solid #7f1d1d; }

/* ── Source citations ── */
.cite-sources {
    font-size: 0.72rem;
    color: #475569;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #1e2433;
}
.cite-sources a { color: #3b82f6 !important; text-decoration: none; }
.cite-sources a:hover { text-decoration: underline; }

/* ── Comparison columns ── */
.compare-col {
    background: #0f111a;
    border: 1px solid #1e2843;
    border-radius: 8px;
    padding: 12px;
    font-size: 0.85rem;
}

/* ── RAGAS quality section ── */
.ragas-section {
    margin-top: 1.25rem;
    padding-top: 1rem;
    border-top: 1px solid #1e2433;
}
.ragas-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}
.ragas-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: #475569;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.ragas-badge {
    font-size: 0.65rem;
    font-weight: 700;
    background: rgba(29,158,117,0.15);
    color: #4ade80;
    padding: 2px 7px;
    border-radius: 4px;
    letter-spacing: 0.05em;
    border: 1px solid rgba(29,158,117,0.25);
}
.rq-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 9px;
}
.rq-label {
    font-size: 0.75rem;
    color: #94a3b8;
    width: 138px;
    flex-shrink: 0;
}
.rq-hint {
    font-size: 0.68rem;
    color: #334155;
    width: 108px;
    flex-shrink: 0;
}
.rq-track {
    flex: 1;
    height: 5px;
    background: #1e2433;
    border-radius: 3px;
    overflow: hidden;
    min-width: 60px;
}
.rq-fill-g { height: 100%; border-radius: 3px; background: #22c55e; }
.rq-fill-a { height: 100%; border-radius: 3px; background: #f59e0b; }
.rq-fill-r { height: 100%; border-radius: 3px; background: #ef4444; }
.rq-score-g { font-size: 0.78rem; font-weight: 600; color: #4ade80; width: 34px; text-align: right; flex-shrink: 0; }
.rq-score-a { font-size: 0.78rem; font-weight: 600; color: #fbbf24; width: 34px; text-align: right; flex-shrink: 0; }
.rq-score-r { font-size: 0.78rem; font-weight: 600; color: #f87171; width: 34px; text-align: right; flex-shrink: 0; }
.rq-warn {
    margin-top: 10px;
    padding: 7px 11px;
    background: rgba(245,158,11,0.08);
    border-left: 2px solid #f59e0b;
    border-radius: 0 5px 5px 0;
    font-size: 0.72rem;
    color: #94a3b8;
    line-height: 1.5;
}
.rq-warn b { color: #fbbf24; }
.rq-ok {
    margin-top: 10px;
    padding: 7px 11px;
    background: rgba(34,197,94,0.06);
    border-left: 2px solid #22c55e;
    border-radius: 0 5px 5px 0;
    font-size: 0.72rem;
    color: #475569;
}
.source-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 8px;
    margin-bottom: 0;
}
.source-card {
    background: #0f111a;
    border: 1px solid #1e2843;
    border-radius: 9px;
    padding: 10px 11px;
}
.source-card-title {
    font-size: 0.75rem;
    font-weight: 500;
    color: #60a8f8;
    line-height: 1.35;
    margin-bottom: 5px;
}
.source-card-section {
    font-size: 0.65rem;
    color: #334155;
    margin-bottom: 5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.source-card-rank {
    font-size: 0.68rem;
    color: #475569;
}
.source-card-rank b { color: #94a3b8; }
</style>
""", unsafe_allow_html=True)



# ── API helpers ────────────────────────────────────────────────────────────────

def api_get(ep):
    try:
        r = httpx.get(f"{API_URL}{ep}", timeout=30)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        st.error(f"API {e.response.status_code}: {e.response.text[:200]}")
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None


def api_post(ep, data, timeout=120):
    try:
        r = httpx.post(f"{API_URL}{ep}", json=data, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        try:
            err_msg = e.response.json().get("detail", e.response.text[:200])
        except:
            err_msg = e.response.text[:200]
        st.session_state._last_api_error = err_msg
        return None
    except Exception as e:
        st.session_state._last_api_error = f"Connection error: {e}"
        return None


# ── Session ────────────────────────────────────────────────────────────────────


def init_session():
    defaults = dict(
        step=1, company_ctx={}, departments=[],
        selected_dept=None, selected_dept_id=None,
        selected_doc_type=None, doc_sec_id=None, sections=[],
        section_questions={}, section_answers={},
        section_contents={}, sec_ids_ordered=[],
        gen_id=None, full_document="",
        active_tab="ask", main_tab="💬 CiteRAG",
        rag_chats={}, rag_active_chat=None,
        docx_bytes_cache=None, docx_cache_doc=None,
        _library_data=None, _answer_drafts={},
        _last_chunks=[],
        _ragas_history=[],         # [{question, scores, timestamp, tool_used}]
        _batch_progress=None,      # {done, total, current_q} — live batch progress
        # ── Agent / Tickets tab ────────────────────────────────────────────────
        agent_tickets=[],          # [{ticket_id, question, status, priority, url, created_at, summary, sources}]
        agent_tickets_loaded=False,
        _pending_ticket_idx=None,  # index of message awaiting ticket creation
        _ticket_created={},        # {msg_idx: ticket_url} — tracks created tickets per message
        agent_memory={},           # {user_name, industry, last_doc, last_intent}
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()
