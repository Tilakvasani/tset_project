import streamlit as st
import uuid as _uuid
import time as _time_mod

def render_citerag_tab(api_get, api_post):
    """
    Renders the CiteRAG Lab (Chat) interface.
    Extracted from the main streamlit_app.py monolith.
    """
    if not st.session_state.rag_chats:
        _c0 = _uuid.uuid4().hex[:8]
        st.session_state.rag_chats[_c0] = {
            "title": "New chat", "messages": [], "created": _time_mod.time()
        }
        st.session_state.rag_active_chat = _c0

    if (not st.session_state.rag_active_chat
            or st.session_state.rag_active_chat not in st.session_state.rag_chats):
        st.session_state.rag_active_chat = next(iter(st.session_state.rag_chats))

    active_id   = st.session_state.rag_active_chat
    active_chat = st.session_state.rag_chats[active_id]
    messages    = active_chat["messages"]

    if not messages:
        st.markdown("""
<div style="text-align:center;padding:3rem 0 1rem">
    <div style="font-size:3rem;margin-bottom:1rem">⚡</div>
    <h2 style="color:#e2e8f0;font-weight:700;margin-bottom:0.5rem">CiteRAG Lab</h2>
    <p style="color:#475569;font-size:0.95rem">Ask questions about your documents · Cite sources · Compare clauses · Analyse legal risk</p>
</div>
""", unsafe_allow_html=True)
        st.divider()
        examples = [
            "What is the notice period in the employment contract?",
            "Compare SOW vs NDA confidentiality clauses",
            "What are the leave policy details?",
            "Summarise the HR policies",
        ]
        c1, c2 = st.columns(2)
        for i, ex in enumerate(examples):
            with (c1 if i % 2 == 0 else c2):
                if st.button(ex, key=f"ex_{i}", use_container_width=True):
                    st.session_state._prefill_q = ex
                    st.rerun()
    else:
        st.caption(f"💬  {active_chat.get('title', 'New chat')}")

    for msg in messages:
        role       = msg["role"]
        text       = msg["content"]
        citations  = msg.get("citations", [])
        confidence = msg.get("confidence", "")

        with st.chat_message(role):
            if role == "assistant" and confidence:
                badge_cls = "cite-high" if confidence == "high" else "cite-medium" if confidence == "medium" else "cite-low"
                badge_label = {"high": "CiteRAG · HIGH", "medium": "CiteRAG · MEDIUM", "low": "CiteRAG · LOW"}.get(confidence, "CiteRAG")
                st.markdown(f'<span class="cite-badge {badge_cls}">{badge_label}</span>', unsafe_allow_html=True)

            if msg.get("tool_used") == "compare" and msg.get("side_a"):
                raw = msg.get("content", "")

                def _sect(text, start_tag, end_tags):
                    if start_tag not in text:
                        return ""
                    part = text.split(start_tag, 1)[1]
                    for tag in end_tags:
                        if tag in part:
                            part = part.split(tag, 1)[0]
                    return part.strip()

                doc_a = msg.get("doc_a", "Document A")
                doc_b = msg.get("doc_b", "Document B")
                doc_a_tag = f"DOCUMENT A -- {doc_a}"
                doc_b_tag = f"DOCUMENT B -- {doc_b}"

                final_answer  = _sect(raw, "FINAL ANSWER", [doc_a_tag, "DOCUMENT_A:"])
                if doc_a_tag in raw:
                    doc_a_content = _sect(raw, doc_a_tag, [doc_b_tag, "COMPARISON TABLE", "GAP IDENTIFIED:"])
                    doc_b_content = _sect(raw, doc_b_tag, ["COMPARISON TABLE", "GAP IDENTIFIED:", "KEY DIFFERENCE:", "COMPARISON INSIGHT:", "SUMMARY:"])
                    comp_table    = _sect(raw, "COMPARISON TABLE", ["GAP IDENTIFIED:", "KEY DIFFERENCE:", "SYSTEMIC ISSUE", "COMPARISON INSIGHT:"])
                else:
                    doc_a_content = msg.get("side_a", "")
                    doc_b_content = msg.get("side_b", "")
                    comp_table    = msg.get("comp_table", "")

                gap_block  = _sect(raw, "GAP IDENTIFIED:", ["KEY DIFFERENCE:", "SYSTEMIC ISSUE", "COMPARISON INSIGHT:", "SUMMARY:"])
                key_diff   = _sect(raw, "KEY DIFFERENCE:", ["SYSTEMIC ISSUE", "COMPARISON INSIGHT:", "SUMMARY:"])
                systemic   = _sect(raw, "SYSTEMIC ISSUE", ["COMPARISON INSIGHT:", "SUMMARY:"])
                insight    = _sect(raw, "COMPARISON INSIGHT:", ["SUMMARY:"])
                summary    = _sect(raw, "SUMMARY:", ["END_NEVER_MATCHES"])

                if final_answer:
                    st.markdown("📋 **FINAL ANSWER:** " + final_answer)
                    st.divider()

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**🔵 {doc_a}**")
                    st.markdown(doc_a_content or msg.get("side_a", ""))
                with col_b:
                    st.markdown(f"**🟢 {doc_b}**")
                    st.markdown(doc_b_content or msg.get("side_b", ""))

                if comp_table:
                    st.divider()
                    st.markdown("**📊 COMPARISON TABLE**")
                    st.markdown(comp_table)

                if gap_block:
                    st.divider()
                    st.markdown("**🔴 GAP IDENTIFIED:**")
                    st.markdown(gap_block)
                if key_diff:
                    st.markdown("**🔑 KEY DIFFERENCE:** " + key_diff)
                if systemic:
                    st.warning("⚠️ **SYSTEMIC ISSUE:** " + systemic)
                if insight:
                    st.divider()
                    st.markdown("**💡 COMPARISON INSIGHT:**")
                    st.markdown(insight)
                if summary:
                    st.divider()
                    st.markdown("**📝 SUMMARY:** " + summary)

            else:
                st.markdown(text)

            if citations and role == "assistant":
                seen, unique = set(), []
                for c in citations:
                    key = c if isinstance(c, str) else c.get("text", "")
                    if key not in seen:
                        seen.add(key)
                        unique.append(c)
                parts = []
                for c in unique:
                    if isinstance(c, dict) and c.get("url"):
                        parts.append(f'<a href="{c["url"]}" target="_blank">{c["text"]}</a>')
                    else:
                        txt = c if isinstance(c, str) else c.get("text", str(c))
                        parts.append(f'<span>{txt}</span>')
                src_html = " &nbsp;·&nbsp; ".join(parts)
                st.markdown(f'<div class="cite-sources">📎 {src_html}</div>', unsafe_allow_html=True)

            if role == "assistant":
                agent_note = msg.get("agent_reply", "")
                if agent_note and msg.get("tool_used") != "agent":
                    is_ticket_created = "✅" in agent_note and "Ticket" in agent_note
                    box_bg  = "rgba(34,197,94,0.07)"  if is_ticket_created else "rgba(59,130,246,0.07)"
                    box_bdr = "#22c55e"                if is_ticket_created else "#3b82f6"
                    box_clr = "#4ade80"                if is_ticket_created else "#93c5fd"
                    st.markdown(
                        f'<div style="margin-top:10px;padding:10px 14px;' +
                        f'background:{box_bg};border-left:3px solid {box_bdr};' +
                        f'border-radius:0 8px 8px 0;font-size:0.83rem;color:{box_clr}">' +
                        agent_note.replace("\n", "<br>") +
                        '</div>',
                        unsafe_allow_html=True,
                    )
                elif msg.get("tool_used") == "agent":
                    st.markdown(
                        '<div style="margin-top:6px">'
                        '<span style="font-size:11px;background:rgba(99,102,241,0.15);color:#a5b4fc;'
                        'padding:2px 8px;border-radius:99px">🤖 Agent</span>'
                        '</div>',
                        unsafe_allow_html=True,
                    )

    _prefill = st.session_state.pop("_prefill_q", "")
    user_q   = st.chat_input("Ask anything...")

    if user_q or _prefill:
        question = (user_q or _prefill).strip() 
        if not messages:
            st.session_state.rag_chats[active_id]["title"] = (
                question[:40] + ("..." if len(question) > 40 else "")
            )
        st.session_state.rag_chats[active_id]["messages"].append(
            {"role": "user", "content": question}
        )
        with st.spinner("Thinking..."):
            res = api_post("/rag/ask", {
                "question":   question,
                "session_id": active_id,
                "top_k":      15,
            }, timeout=120)
        if res:
            ai_msg = {
                "role":           "assistant",
                "content":        res.get("answer", "No answer returned."),
                "citations":      res.get("citations", []),
                "confidence":     res.get("confidence", ""),
                "tool_used":      res.get("tool_used", ""),
                "ticket_pending": res.get("ticket_pending", False),
                "orig_question":  question,
                "ticket_id":      res.get("ticket_id"),
                "ticket_url":     res.get("ticket_url"),
                "agent_reply":    res.get("agent_reply", ""),
            }
            if res.get("tool_used") == "compare":
                ai_msg.update({
                    "side_a":      res.get("side_a", ""),
                    "side_b":      res.get("side_b", ""),
                    "comp_table":  res.get("comp_table", ""),
                    "summary":     res.get("summary", ""),
                    "doc_a":       res.get("doc_a", "Document A"),
                    "doc_b":       res.get("doc_b", "Document B"),
                })
            st.session_state._last_chunks    = res.get("chunks") or res.get("_raw_chunks", [])
            st.session_state._last_not_found = (not res.get("chunks") and bool(res.get("_raw_chunks")))
        else:
            err = st.session_state.get("_last_api_error", "Could not reach the RAG service. Make sure the backend is running.")
            if "_last_api_error" in st.session_state:
                del st.session_state["_last_api_error"]

            ai_msg = {
                "role":      "assistant",
                "content":   f"⚠️ **Error:** {err}",
                "citations": [],
            }
            st.session_state._last_chunks    = []
            st.session_state._last_not_found = False
        st.session_state.rag_chats[active_id]["messages"].append(ai_msg)
        st.rerun()

    chunks       = st.session_state.get("_last_chunks", [])
    not_found    = st.session_state.get("_last_not_found", False)
    toggle_label = "🔍 Show Sources" if not not_found else "🔍 Show Sources (searched but not found)"

    if chunks:
        if st.toggle(toggle_label, value=False, key="show_retrieval"):
            if not_found:
                st.markdown(
                    '<div style="background:#1a1f2e;border:1px solid #ef444430;border-radius:8px;'
                    'padding:8px 12px;margin-bottom:10px;font-size:12px;color:#f87171">'
                    '⚠️ These were the closest documents found — none contained a confident answer.'
                    '</div>',
                    unsafe_allow_html=True,
                )

            seen_docs = {}
            for c in chunks:
                title   = c.get("doc_title", "")
                score   = c.get("score", 0)
                page_id = c.get("notion_page_id", "")
                section = c.get("section", c.get("heading", ""))
                if title and title not in seen_docs:
                    seen_docs[title] = {
                        "score":   score,
                        "page_id": page_id,
                        "section": section,
                    }
            top5 = sorted(
                seen_docs.items(), key=lambda x: x[1]["score"], reverse=True
            )[:5]

            if top5:
                cards_html = (
                    '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));'
                    'gap:8px;margin-bottom:12px">'
                )
                for i, (doc, info) in enumerate(top5):
                    score   = info["score"]
                    page_id = info["page_id"]
                    section = info.get("section", "")
                    url     = f"https://www.notion.so/{page_id}" if page_id else ""
                    dot_col = "#22c55e" if score >= 0.6 else "#f59e0b" if score >= 0.4 else "#ef4444"
                    title_html = (
                        f'<a href="{url}" target="_blank" '
                        f'style="color:#60a8f8;text-decoration:none;font-size:12px;'
                        f'font-weight:500;line-height:1.35">{doc}</a>'
                        if url else
                        f'<span style="color:#60a8f8;font-size:12px;font-weight:500">{doc}</span>'
                    )
                    cards_html += (
                        f'<div style="background:#0f111a;border:1px solid #1e2843;'
                        f'border-radius:9px;padding:10px 11px">'
                        f'<div style="display:flex;align-items:center;gap:5px;margin-bottom:5px">'
                        f'<span style="width:7px;height:7px;border-radius:50%;background:{dot_col};flex-shrink:0"></span>'
                        f'{title_html}'
                        f'</div>'
                        f'<div style="font-size:10px;color:#334155;margin-bottom:5px;white-space:nowrap;'
                        f'overflow:hidden;text-overflow:ellipsis">{section}</div>'
                        f'<div style="font-size:11px;color:#475569">Rank {i+1} · '
                        f'<b style="color:#94a3b8">{score:.3f}</b></div>'
                        f'</div>'
                    )
                cards_html += "</div>"
                st.markdown(cards_html, unsafe_allow_html=True)
            elif not_found:
                st.info("No documents were retrieved — this topic may not exist in any ingested document yet.")
