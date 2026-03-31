import streamlit as st

def render_tickets_tab(api_get, api_post):
    """
    Renders the Tickets (Agent Memory & Ticket Viewer) interface.
    Extracted from the main streamlit_app.py monolith.
    Tickets are created when CiteRAG retrieval confidence is low or manually requested.
    """
    import json as _aj

    # ── Page header ────────────────────────────────────────────────────────────
    st.markdown("""
<div style="padding:0 0 0.5rem">
  <h2 style="color:#e2e8f0;font-weight:700;margin-bottom:0.2rem">🎫 Tickets</h2>
  <p style="color:#475569;font-size:0.88rem;margin:0">
    Knowledge-gap tickets — say <b style="color:#93c5fd">"create a ticket"</b>,
    <b style="color:#93c5fd">"raise a ticket"</b> or <b style="color:#93c5fd">"open a case"</b>
    in <b style="color:#93c5fd">💬 CiteRAG</b> to log a missing answer
  </p>
</div>
""", unsafe_allow_html=True)
    st.divider()

    # ── Two-column layout ──────────────────────────────────────────────────────
    col_mem, col_tix = st.columns([1, 2], gap="large")

    # ════════════════════════════════════════════════════════════
    #  LEFT — 🧠 Memory panel
    # ════════════════════════════════════════════════════════════
    with col_mem:
        st.markdown("""
<div style="font-size:11px;font-weight:600;color:#475569;letter-spacing:0.08em;
            text-transform:uppercase;margin-bottom:10px">🧠 Session Memory</div>
""", unsafe_allow_html=True)

        mem = st.session_state.get("agent_memory", {})

        # Live memory chips
        if mem:
            chips_html = ""
            _chip = lambda ico, val: (
                f'<span style="display:inline-flex;align-items:center;gap:4px;'
                f'background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);'
                f'border-radius:20px;padding:3px 10px;font-size:11px;color:#93c5fd;'
                f'margin:2px 3px">{ico} {val}</span>'
            )
            if mem.get("user_name"):
                chips_html += _chip("👤", mem["user_name"])
            if mem.get("industry"):
                chips_html += _chip("🏭", mem["industry"])
            if mem.get("last_intent"):
                chips_html += _chip("🎯", mem["last_intent"])
            if mem.get("last_doc"):
                chips_html += _chip("📄", mem["last_doc"][:22])
            st.markdown(f'<div style="margin-bottom:14px">{chips_html}</div>', unsafe_allow_html=True)
        else:
            st.caption("No memory yet — ask a question in 💬 CiteRAG to populate this.")

        st.divider()

        # Context hints (pre-fill memory)
        st.markdown("""
<div style="font-size:11px;font-weight:600;color:#475569;letter-spacing:0.08em;
            text-transform:uppercase;margin-bottom:8px">⚙️ Context Hints</div>
""", unsafe_allow_html=True)
        st.caption("Pre-fill memory so the agent knows who you are before the first question.")

        _hn = st.text_input("Your name", value=mem.get("user_name", ""),
                            placeholder="e.g. Rahul", key="ag_hint_name")
        _hi = st.text_input("Industry / department", value=mem.get("industry", ""),
                            placeholder="e.g. Technology / HR", key="ag_hint_industry")

        if st.button("💾 Save Hints", key="ag_save_hints", use_container_width=True):
            st.session_state.agent_memory["user_name"] = _hn.strip()
            st.session_state.agent_memory["industry"]  = _hi.strip()
            
            # ── SYNC TO BACKEND ──────────────────
            res_sync = api_post("/agent/memory", {
                "session_id": st.session_state.rag_active_chat,
                "memory": {
                    "user_name": _hn.strip(),
                    "industry":  _hi.strip()
                }
            })
            if res_sync and "error" not in res_sync:
                st.success("Hints saved & synced to backend!")
            else:
                st.error("Sync failed.")
            st.rerun()

        st.divider()

        # Sync memory from backend
        if st.button("↺ Sync from Backend", key="ag_sync_mem", use_container_width=True):
            _mres = api_get(f"/agent/memory?session_id={st.session_state.rag_active_chat}")
            if _mres and "error" not in _mres:
                st.session_state.agent_memory.update(_mres.get("memory", {}))
                st.success("Memory synced!")
                st.rerun()
            else:
                st.warning("⚠️ `/api/agent/memory` not yet implemented or sync failed.")

        # Quick stats
        st.divider()
        _tix = st.session_state.get("agent_tickets", [])
        _open_n = len([t for t in _tix if t.get("status") == "Open"])
        _tot_n  = len(_tix)
        _c1, _c2 = st.columns(2)
        _c1.metric("Total Tickets", _tot_n)
        _c2.metric("Open", _open_n)

    # ════════════════════════════════════════════════════════════
    #  RIGHT — 🎫 My Tickets
    # ════════════════════════════════════════════════════════════
    with col_tix:
        # Header row
        _th1, _th2, _th3 = st.columns([2, 1, 1])
        with _th1:
            st.markdown("""
<div style="font-size:11px;font-weight:600;color:#475569;letter-spacing:0.08em;
            text-transform:uppercase;margin-bottom:10px">🎫 Knowledge-Gap Tickets</div>
""", unsafe_allow_html=True)
        with _th2:
            _tix_filter = st.selectbox(
                "Status filter",
                ["All", "Open", "In Progress", "Resolved"],
                key="ag_tix_filter",
                label_visibility="collapsed",
            )
        with _th3:
            if st.button("↺ Refresh", key="ag_refresh_tix", use_container_width=True):
                st.session_state.agent_tickets_loaded = False

        # Load tickets from backend (Notion)
        if not st.session_state.agent_tickets_loaded:
            with st.spinner("Loading tickets from Notion…"):
                _td = api_get("/agent/tickets")
            if _td and "error" not in _td:
                st.session_state.agent_tickets = _td.get("tickets", [])
                st.session_state.agent_tickets_loaded = True
            else:
                _err = _td.get("error", "Unknown") if _td else "Backend unreachable"
                st.info(f"ℹ️ Tickets endpoint not yet active: `{_err}`")

        _all_tix = st.session_state.agent_tickets
        _show_tix = (
            _all_tix if _tix_filter == "All"
            else [t for t in _all_tix if t.get("status", "") == _tix_filter]
        )

        if not _all_tix:
            st.markdown("""
<div style="text-align:center;padding:3rem 1rem;background:#0f111a;
            border:1px dashed #1e2843;border-radius:12px;margin-top:8px">
  <div style="font-size:2rem;margin-bottom:0.6rem">🎫</div>
  <div style="color:#475569;font-size:0.85rem;line-height:1.6">
    No tickets yet.<br>
    Ask a question in <b style="color:#93c5fd">💬 CiteRAG</b>, then say:<br>
    <b style="color:#a5b4fc">"create a ticket"</b> · <b style="color:#a5b4fc">"raise a ticket"</b> · <b style="color:#a5b4fc">"open a case"</b><br>
    Duplicate questions are automatically detected before creating a new ticket.
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            # Summary metrics bar
            _op  = len([t for t in _all_tix if t.get("status") == "Open"])
            _ip  = len([t for t in _all_tix if t.get("status") == "In Progress"])
            _dn  = len([t for t in _all_tix if t.get("status") == "Resolved"])
            _sm1, _sm2, _sm3, _sm4 = st.columns(4)
            _sm1.metric("Total",       len(_all_tix))
            _sm2.metric("Open",        _op)
            _sm3.metric("In Progress", _ip)
            _sm4.metric("Resolved",    _dn)
            st.write("")

            if not _show_tix:
                st.info(f"No tickets with status '{_tix_filter}'.")
            else:
                for _t in _show_tix:
                    _ts   = _t.get("status", "Open")
                    _tp   = _t.get("priority", "Medium")
                    _tq   = _t.get("question", "—")
                    _tid  = _t.get("ticket_id", "—")
                    _tts  = _t.get("created_at", "")
                    _turl = _t.get("url", "")
                    _tsum = _t.get("summary", "")
                    _tsrc = _t.get("attempted_sources", [])

                    # Colour mappings
                    _s_col = {"Open": "#f87171", "In Progress": "#fbbf24", "Resolved": "#4ade80"}.get(_ts, "#94a3b8")
                    _s_bg  = {"Open": "rgba(239,68,68,0.08)", "In Progress": "rgba(245,158,11,0.08)", "Resolved": "rgba(34,197,94,0.08)"}.get(_ts, "rgba(148,163,184,0.08)")
                    _s_bd  = {"Open": "rgba(239,68,68,0.25)", "In Progress": "rgba(245,158,11,0.25)", "Resolved": "rgba(34,197,94,0.25)"}.get(_ts, "rgba(148,163,184,0.25)")
                    _p_col = {"High": "#f87171", "Medium": "#fbbf24", "Low": "#4ade80"}.get(_tp, "#94a3b8")

                    with st.container(border=True):
                        _tca, _tcb = st.columns([4, 1])
                        with _tca:
                            st.markdown(
                                f'<span style="background:{_s_bg};border:1px solid {_s_bd};'
                                f'border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600;'
                                f'color:{_s_col}">{_ts}</span>'
                                f'&nbsp;<span style="font-size:11px;color:{_p_col};'
                                f'font-weight:600">{_tp}</span>'
                                f'&nbsp;<span style="background:rgba(51,65,85,0.06);'
                                f'padding:2px 6px;border-radius:4px;font-family:monospace;'
                                f'font-size:11px;color:#475569;border:1px solid rgba(51,65,85,0.12)">'
                                f'#{_tid}</span>'
                                + (f'&nbsp;<span style="font-size:11px;color:#64748b"> · {(_tts[:10] if _tts else "")}</span>' if _tts else ""),
                                unsafe_allow_html=True,
                            )
                            st.markdown(f"**{_tq[:110]}{'…' if len(_tq) > 110 else ''}**")
                            if _tsum: st.caption(_tsum[:200])

                        with _tcb:
                            if _turl: st.link_button("Notion →", _turl, use_container_width=True)

                        if _tsrc:
                            with st.expander("📎 Attempted sources", expanded=False):
                                for _s in _tsrc: st.markdown(f"- {_s}")

                        # Inline status update
                        _opts = ["Open", "In Progress", "Resolved"]
                        _curidx = _opts.index(_ts) if _ts in _opts else 0
                        _wkey = _t.get("page_id", _tid).replace("-", "")[:16]
                        _col_sel, _col_btn = st.columns([2, 1])
                        with _col_sel:
                            _new_s = st.selectbox("Update status", _opts, index=_curidx, key=f"tix_sel_{_wkey}", label_visibility="collapsed")
                        with _col_btn:
                            if _new_s != _ts:
                                if st.button("✅ Update", key=f"tix_upd_{_wkey}", use_container_width=True, type="primary"):
                                    _ur = api_post("/agent/tickets/update", {"ticket_id": _tid, "status": _new_s})
                                    if _ur and "error" not in _ur:
                                        st.success(f"Ticket #{_tid} → {_new_s}")
                                        st.session_state.agent_tickets_loaded = False
                                        st.rerun()
                                    else:
                                        st.error("Update failed.")

    # ── Backend endpoint reference (collapsible) ───────────────────────────────
    st.divider()
    with st.expander("🔧 Backend endpoints reference"):
        st.markdown("""
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/agent/tickets` | GET | Fetch all tickets from Notion ticket DB |
| `/api/agent/tickets/update` | POST | Update ticket status in Notion |
| `/api/agent/memory` | GET | Read LangGraph thread memory for current user |
""")
