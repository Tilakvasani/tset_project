"""
DocForge AI x CiteRAG Lab — streamlit_app.py  v12.0
Orchestrator: sets up page config, CSS, session state, sidebar,
then delegates each tab to its own module in ui/tabs/.

Tab modules:
  ui/tabs/citerag.py    — 💬 CiteRAG (ask, compare, citations)
  ui/tabs/library.py    — 📚 Document Library
  ui/tabs/ragas_lab.py  — 📊 RAGAS Evaluation
  ui/tabs/docforge.py   — ⚡ DocForge Generator (5-step wizard)
  ui/tabs/tickets.py    — 🎫 Knowledge-Gap Tickets
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Shared setup (CSS, API helpers, init_session) ─────────────────────────────
from ui.tabs.shared import st, httpx, api_get, api_post, API_URL, DOCX_AVAILABLE, init_session

# ── Tab renderers ──────────────────────────────────────────────────────────────
from ui.tabs import citerag, library, ragas_lab, docforge, tickets

# ── Page config (must be first Streamlit call) ─────────────────────────────────
# Already called inside shared.py on import — do NOT call again here.

# ── Session state initialisation ──────────────────────────────────────────────
init_session()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    import time as _t, uuid as _u

    st.markdown("## ⚡ DocForge AI")
    st.caption("Generate · Ask · Discover")
    st.divider()

    def _switch_tab():
        tab = st.session_state.main_tab
        if "DocForge" in tab:
            st.session_state.active_tab = "generate"
        elif "Library" in tab:
            st.session_state.active_tab = "library"
        elif "RAGAS" in tab:
            st.session_state.active_tab = "ragas"
        elif "Ticket" in tab:
            st.session_state.active_tab = "agent"
        else:
            st.session_state.active_tab = "ask"

    st.radio(
        "Mode",
        ["💬 CiteRAG", "⚡ DocForge", "📚 Library", "📊 RAGAS", "🎫 Tickets"],
        label_visibility="collapsed",
        key="main_tab",
        horizontal=False,
        on_change=_switch_tab,
    )

    st.divider()

    # ── CiteRAG: Chat history ──────────────────────────────────────────────────
    if st.session_state.active_tab == "ask":

        if not st.session_state.rag_chats:
            _c0 = _u.uuid4().hex[:8]
            st.session_state.rag_chats[_c0] = {
                "title": "New chat", "messages": [], "created": _t.time()
            }
            st.session_state.rag_active_chat = _c0

        if st.button("＋  New Chat", use_container_width=True,
                     key="sb_new_chat", type="primary"):
            _cn = _u.uuid4().hex[:8]
            st.session_state.rag_chats[_cn] = {
                "title": "New chat", "messages": [], "created": _t.time()
            }
            st.session_state.rag_active_chat = _cn
            st.rerun()

        st.markdown("###### Recent")

        _sorted = sorted(
            st.session_state.rag_chats.items(),
            key=lambda x: x[1].get("created", 0),
            reverse=True,
        )

        for _cid, _chat in _sorted:
            _active = _cid == st.session_state.rag_active_chat
            _title  = _chat["title"][:22] + ("…" if len(_chat["title"]) > 22 else "")
            _msgs   = len([m for m in _chat["messages"] if m["role"] == "user"])
            _label  = f"{'💬' if _msgs else '🆕'}  {_title}"

            if st.session_state.get(f"renaming_{_cid}"):
                _new = st.text_input(
                    "", value=_chat["title"],
                    key=f"rename_input_{_cid}",
                    label_visibility="collapsed",
                    placeholder="Enter new name…",
                )
                _r1, _r2 = st.columns(2)
                with _r1:
                    if st.button("✅ Save", key=f"save_ren_{_cid}",
                                 use_container_width=True, type="primary"):
                        if _new.strip():
                            st.session_state.rag_chats[_cid]["title"] = _new.strip()
                        del st.session_state[f"renaming_{_cid}"]
                        st.rerun()
                with _r2:
                    if st.button("✕ Cancel", key=f"cancel_ren_{_cid}",
                                 use_container_width=True):
                        del st.session_state[f"renaming_{_cid}"]
                        st.rerun()
            else:
                if st.button(
                    _label,
                    key=f"chat_{_cid}",
                    use_container_width=True,
                    type="primary" if _active else "secondary",
                ):
                    st.session_state.rag_active_chat = _cid
                    st.rerun()

                if _active:
                    _a, _b = st.columns(2)
                    with _a:
                        if st.button("✏️ Rename", key=f"ren_{_cid}",
                                     use_container_width=True):
                            st.session_state[f"renaming_{_cid}"] = True
                            st.rerun()
                    with _b:
                        if st.button("🗑 Delete", key=f"del_{_cid}",
                                     use_container_width=True, type="primary"):
                            del st.session_state.rag_chats[_cid]
                            for _k in list(st.session_state.keys()):
                                if _k.endswith(f"_{_cid}"):
                                    st.session_state.pop(_k, None)
                            if st.session_state.rag_active_chat == _cid:
                                st.session_state.rag_active_chat = (
                                    next(iter(st.session_state.rag_chats))
                                    if st.session_state.rag_chats else None
                                )
                            # Clear chunks + RAGAS so Show Sources toggle disappears
                            st.session_state._last_chunks       = []
                            st.session_state._last_ragas_scores = None
                            st.rerun()

    # ── DocForge: Step progress ────────────────────────────────────────────────
    if st.session_state.active_tab == "generate":
        st.markdown("###### Steps")
        steps = [
            (1, "🏢", "Setup"),
            (2, "❓", "Questions"),
            (3, "✍️", "Answers"),
            (4, "⚙️", "Generate"),
            (5, "💾", "Export"),
        ]
        cur = st.session_state.step
        for n, emoji, lbl in steps:
            if n < cur:
                st.markdown(f"✅  ~~Step {n} — {lbl}~~")
            elif n == cur:
                st.markdown(f"**{emoji}  Step {n} — {lbl}**")
            else:
                st.markdown(f"⬜  Step {n} — {lbl}")

        st.divider()
        ctx = st.session_state.company_ctx
        if ctx.get("company_name"):
            st.markdown(f"🏢 **{ctx['company_name']}**")
            st.caption(f"{ctx.get('industry','')} · {ctx.get('region','')}")
        if st.session_state.selected_doc_type:
            st.caption(f"📄 {st.session_state.selected_doc_type}")
        if st.session_state.sections:
            done_n  = len(st.session_state.section_contents)
            total_n = len(st.session_state.sections)
            st.progress(
                done_n / total_n if total_n else 0,
                text=f"{done_n} / {total_n} sections done",
            )
        st.divider()
        if st.button("↺  Start Over", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  CITRAG LAB
# ══════════════════════════════════════════════════════════════════════════════


# ── Tab routing ────────────────────────────────────────────────────────────────
_tab = st.session_state.active_tab

if _tab == "ask":
    citerag.render()

elif _tab == "library":
    library.render()

elif _tab == "ragas":
    ragas_lab.render()

elif _tab == "generate":
    docforge.render()

elif _tab == "agent":
    tickets.render()