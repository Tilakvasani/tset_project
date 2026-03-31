"""
DocForge AI x CiteRAG Lab -- streamlit_app.py  v12.0
Clean Claude-style UI. Modular Architecture.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import httpx

# Import Tab Components
from ui.components.citerag_tab import render_citerag_tab
from ui.components.library_tab import render_library_tab
from ui.components.ragas_tab import render_ragas_tab
from ui.components.docforge_tab import render_docforge_tab
from ui.components.tickets_tab import render_tickets_tab

try:
    from docx_builder import build_docx
    DOCX_AVAILABLE = True
except ImportError:
    from typing import Any
    def build_docx(*args: Any, **kwargs: Any) -> None: pass
    DOCX_AVAILABLE = False

API_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="DocForge AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ──────────────────────────────────────────────────────────────────
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
/* ... existing RAGAS styles ... */
</style>
""", unsafe_allow_html=True)

# ── API helpers ────────────────────────────────────────────────────────────────
def api_get(ep):
    try:
        r = httpx.get(f"{API_URL}{ep}", timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API Get Error: {e}")
        return None

def api_post(ep, data, timeout=120):
    try:
        r = httpx.post(f"{API_URL}{ep}", json=data, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.session_state._last_api_error = str(e)
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
        agent_tickets=[],
        agent_tickets_loaded=False,
        _pending_ticket_idx=None,
        _ticket_created={},
        agent_memory={},
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    import time as _t, uuid as _u
    st.markdown("## ⚡ DocForge AI")
    st.caption("Generate · Ask · Discover")
    st.divider()

    def _switch_tab():
        tab = st.session_state.main_tab
        if "DocForge" in tab:   st.session_state.active_tab = "generate"
        elif "Library" in tab: st.session_state.active_tab = "library"
        elif "Evaluation" in tab:   st.session_state.active_tab = "ragas"
        elif "Ticket" in tab:  st.session_state.active_tab = "agent"
        else:                  st.session_state.active_tab = "ask"

    st.radio(
        "Mode",
        ["💬 CiteRAG", "⚡ DocForge", "📚 Library", "📊 Evaluation", "🎫 Tickets"],
        label_visibility="collapsed",
        key="main_tab",
        horizontal=False,
        on_change=_switch_tab,
    )

    st.divider()

    # Chat history logic (CiteRAG specific sidebar)
    if st.session_state.active_tab == "ask":
        if not st.session_state.rag_chats:
            _c0 = _u.uuid4().hex[:8]
            st.session_state.rag_chats[_c0] = {"title": "New chat", "messages": [], "created": _t.time()}
            st.session_state.rag_active_chat = _c0

        if st.button("＋  New Chat", use_container_width=True, type="primary"):
            _cn = _u.uuid4().hex[:8]
            st.session_state.rag_chats[_cn] = {"title": "New chat", "messages": [], "created": _t.time()}
            st.session_state.rag_active_chat = _cn
            st.rerun()

        _sorted = sorted(st.session_state.rag_chats.items(), key=lambda x: x[1].get("created", 0), reverse=True)
        for _cid, _chat in _sorted:
            _active = _cid == st.session_state.rag_active_chat
            if st.button(f"{'💬' if _chat['messages'] else '🆕'}  {_chat['title'][:22]}", key=f"ch_{_cid}", use_container_width=True, type="primary" if _active else "secondary"):
                st.session_state.rag_active_chat = _cid
                st.rerun()

    # Step progress (DocForge specific sidebar)
    sidebar_progress_bar = None
    if st.session_state.active_tab == "generate":
        st.markdown("###### Steps")
        steps = [(1, "🏢", "Setup"), (2, "❓", "Questions"), (3, "✍️", "Answers"), (4, "⚙️", "Generate"), (5, "💾", "Export")]
        for n, emoji, lbl in steps:
            if n < st.session_state.step: st.markdown(f"✅  ~~Step {n} — {lbl}~~")
            elif n == st.session_state.step: st.markdown(f"**{emoji}  Step {n} — {lbl}**")
            else: st.markdown(f"⬜  Step {n} — {lbl}")
        
        if st.session_state.sections:
            sidebar_progress_bar = st.progress(len(st.session_state.section_contents) / len(st.session_state.sections))

    st.divider()
    if st.button("↺  Start Over", use_container_width=True):
        sa, sm = st.session_state.active_tab, st.session_state.main_tab
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.session_state.active_tab, st.session_state.main_tab = sa, sm
        st.rerun()

# ── Main Content Area ──────────────────────────────────────────────────────────
if st.session_state.active_tab == "ask":
    render_citerag_tab(api_get, api_post)

elif st.session_state.active_tab == "library":
    render_library_tab(api_get, api_post)

elif st.session_state.active_tab == "ragas":
    render_ragas_tab(api_get, api_post)

elif st.session_state.active_tab == "generate":
    render_docforge_tab(api_get, api_post, DOCX_AVAILABLE, build_docx, init_session, sidebar_progress_bar)

elif st.session_state.active_tab == "agent":
    render_tickets_tab(api_get, api_post)