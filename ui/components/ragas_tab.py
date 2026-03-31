import streamlit as st

def _ragas_bar_color(v):
    if v is None:
        return "#334155", "#475569"
    if v >= 0.85:
        return "#22c55e", "#4ade80"
    if v >= 0.70:
        return "#f59e0b", "#fbbf24"
    return "#ef4444", "#f87171"

def _render_ragas_scores(scores, title="", timestamp=""):
    """Render a full RAGAS score panel."""
    if not scores:
        return

    metrics = [
        ("Faithfulness",      scores.get("faithfulness"),      "no hallucination",
         "Answer is grounded solely in the retrieved documents."),
        ("Answer Relevancy",  scores.get("answer_relevancy"),   "on-topic answer",
         "Answer directly addresses the question asked."),
        ("Context Precision", scores.get("context_precision"),  "clean retrieval",
         "Retrieved chunks are relevant — no noise from unrelated documents."),
        ("Context Recall",    scores.get("context_recall"),     "full coverage",
         "All relevant information from ground-truth was retrieved."),
    ]

    avg_vals   = [m[1] for m in metrics if m[1] is not None]
    avg_score  = round(sum(avg_vals) / len(avg_vals), 2) if avg_vals else None
    avg_col    = "#4ade80" if (avg_score or 0) >= 0.85 else "#fbbf24" if (avg_score or 0) >= 0.70 else "#f87171"

    header_html = (
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'margin-bottom:16px">'
        f'<div style="font-size:13px;font-weight:600;color:#cbd5e1">'
        f'{title or "Scores"}</div>'
        f'<div style="display:flex;align-items:center;gap:10px">'
    )
    if timestamp:
        header_html += f'<span style="font-size:11px;color:#475569">{timestamp}</span>'
    if avg_score is not None:
        header_html += (
            f'<span style="font-size:12px;font-weight:700;color:{avg_col};'
            f'background:rgba(255,255,255,0.04);padding:3px 10px;border-radius:5px;'
            f'border:1px solid {avg_col}33">avg {avg_score:.2f}</span>'
        )
    header_html += '</div></div>'

    rows_html  = ""
    warn_lines = []
    has_null   = False

    for label, val, hint, explanation in metrics:
        if val is None:
            has_null = True
            rows_html += (
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;opacity:0.45">'
                f'<span style="font-size:12px;color:#94a3b8;width:150px;flex-shrink:0">{label}</span>'
                f'<span style="font-size:11px;color:#334155;width:110px;flex-shrink:0">{hint}</span>'
                f'<div style="flex:1;height:5px;background:#1e2433;border-radius:3px;min-width:80px">'
                f'<div style="width:0%;height:100%;background:#334155;border-radius:3px"></div></div>'
                f'<span style="font-size:11px;color:#334155;width:38px;text-align:right;flex-shrink:0">n/a</span>'
                f'</div>'
            )
            continue

        pct                = int(val * 100)
        bar_col, txt_col   = _ragas_bar_color(val)
        score_str          = f"{val:.2f}"

        if val < 0.70:
            if "faith" in label.lower():
                warn_lines.append("&#9888; <b>Faithfulness low</b> — answer may contain claims not grounded in documents.")
            elif "precision" in label.lower():
                warn_lines.append("&#9888; <b>Context precision low</b> — retriever fetched irrelevant chunks.")
            elif "recall" in label.lower():
                warn_lines.append("&#9888; <b>Context recall low</b> — relevant chunks may have been missed.")
            elif "relev" in label.lower():
                warn_lines.append("&#9888; <b>Answer relevancy low</b> — answer drifted off-topic.")

        rows_html += (
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">'
            f'<span style="font-size:12px;color:#94a3b8;width:150px;flex-shrink:0">{label}</span>'
            f'<span style="font-size:11px;color:#334155;width:110px;flex-shrink:0">{hint}</span>'
            f'<div style="flex:1;height:5px;background:#1e2433;border-radius:3px;overflow:hidden;min-width:80px">'
            f'<div style="width:{pct}%;height:100%;background:{bar_col};border-radius:3px"></div></div>'
            f'<span style="font-size:12px;font-weight:600;color:{txt_col};width:38px;text-align:right;flex-shrink:0">{score_str}</span>'
            f'</div>'
        )

    feedback_html = ""
    if warn_lines:
        feedback_html = (
            f'<div style="margin-top:10px;padding:8px 12px;background:rgba(245,158,11,0.08);'
            f'border-left:2px solid #f59e0b;border-radius:0 5px 5px 0;font-size:12px;color:#94a3b8;line-height:1.7">'
            + "<br>".join(warn_lines) + '</div>'
        )
    elif avg_vals:
        feedback_html = (
            '<div style="margin-top:10px;padding:8px 12px;background:rgba(34,197,94,0.06);'
            'border-left:2px solid #22c55e;border-radius:0 5px 5px 0;font-size:12px;color:#475569">'
            '✓ All quality metrics look good.</div>'
        )

    if has_null:
        feedback_html += (
            '<div style="margin-top:8px;font-size:11px;color:#334155">'
            '* Context recall shown as n/a — no matching ground truth in qa_dataset.json for this question.</div>'
        )

    st.markdown(
        f'<div style="background:#131722;border:1px solid #1e2843;border-radius:12px;padding:18px 20px;margin-bottom:12px">'
        + header_html + rows_html + feedback_html +
        '</div>',
        unsafe_allow_html=True,
    )

def render_ragas_tab(api_get, api_post):
    """
    Renders the RAGAS Evaluation interface.
    Extracted from the main streamlit_app.py monolith.
    """
    st.markdown("""
<div style="padding:0 0 1rem">
    <h2 style="color:#e2e8f0;font-weight:700;margin-bottom:0.25rem">📊 RAGAS Evaluation</h2>
    <p style="color:#475569;font-size:0.9rem">Real answer quality scores — faithfulness, relevancy, precision, recall</p>
</div>
""", unsafe_allow_html=True)
    st.divider()

    # ── Section 1: Latest scores (from most recent CiteRAG answer) ─────────────
    last_scores = st.session_state.get("_last_ragas_scores")
    if last_scores:
        st.markdown("#### 🔬 Latest Answer Quality")
        _render_ragas_scores(last_scores, title="Most recent question")

    # ── Section 3: Batch Evaluation ───────────────────────────────────────────
    st.divider()
    st.markdown("#### 🗂 Batch Evaluation")
    st.caption("Run RAGAS on multiple questions at once — add rows manually or import a JSON file.")

    # ── Init batch state ──────────────────────────────────────────────────────
    if "batch_rows" not in st.session_state:
        st.session_state.batch_rows = [{"question": "", "ground_truth": ""}]
    if "batch_results" not in st.session_state:
        st.session_state.batch_results = []
    if "batch_running" not in st.session_state:
        st.session_state.batch_running = False

    with st.container(border=True):
        # ── JSON import ────────────────────────────────────────────────────────
        with st.expander("📥 Import from JSON", expanded=False):
            st.caption(
                'Expected format: `[{"question": "...", "ground_truth": "..."}, ...]`  '
                '— `ground_truth` is optional in each item.'
            )

            uploaded = st.file_uploader(
                "Upload JSON file",
                type=["json"],
                key="batch_json_upload",
                label_visibility="collapsed",
            )
            
            if uploaded:
                import json as _json
                try:
                    raw_data = _json.loads(uploaded.read().decode("utf-8"))
                    if isinstance(raw_data, list):
                        parsed_rows = []
                        for item in raw_data:
                            if isinstance(item, dict) and item.get("question", "").strip():
                                parsed_rows.append({
                                    "question":     item.get("question", "").strip(),
                                    "ground_truth": item.get("ground_truth", "").strip(),
                                })
                        if parsed_rows:
                            st.session_state.batch_rows = parsed_rows
                            st.session_state.batch_results = []
                            st.success(f"Loaded {len(parsed_rows)} questions from JSON.")
                        else:
                            st.error("No valid questions found in JSON.")
                    else:
                        st.error("JSON must be a list of objects.")
                except Exception as _je:
                    st.error(f"JSON parse error: {_je}")

        # ── Manual rows ────────────────────────────────────────────────────────
        st.markdown("**Questions**")
        rows_to_delete = []
        for _ri, _row in enumerate(st.session_state.batch_rows):
            _rc1, _rc2, _rc3 = st.columns([3, 3, 0.5])
            with _rc1:
                _q_val = st.text_input(f"Q {_ri}", value=_row["question"], placeholder="Enter evaluation question (should be answerable from your documents)", key=f"batch_q_{_ri}", label_visibility="collapsed")
                st.session_state.batch_rows[_ri]["question"] = _q_val
            with _rc2:
                _gt_val = st.text_input(f"GT {_ri}", value=_row["ground_truth"], placeholder="Enter reference answer (used for RAGAS scoring)", key=f"batch_gt_{_ri}", label_visibility="collapsed")
                st.session_state.batch_rows[_ri]["ground_truth"] = _gt_val
            with _rc3:
                if len(st.session_state.batch_rows) > 1:
                    if st.button("✕", key=f"batch_del_{_ri}"):
                        rows_to_delete.append(_ri)

        if rows_to_delete:
            for _idx in sorted(rows_to_delete, reverse=True):
                st.session_state.batch_rows.pop(_idx)
            st.session_state.batch_results = []
            st.rerun()

        _ba1, _ba2 = st.columns([1, 3])
        with _ba1:
            if st.button("＋ Add Row", key="batch_add_row"):
                st.session_state.batch_rows.append({"question": "", "ground_truth": ""})
                st.rerun()
        with _ba2:
            st.caption(f"{len(st.session_state.batch_rows)} question ready for evaluation")

        _valid_rows = [r for r in st.session_state.batch_rows if r["question"].strip() and r['ground_truth'].strip()]

        _bp = st.session_state.get("_batch_progress")
        if _bp and _bp.get("running"):
            _done  = _bp["done"]
            _total = _bp["total"]
            st.progress(_done/_total, text=f"⏳ Running {_done}/{_total}: {_bp.get('current_q', '')[:55]}…")

        if st.button(f"▶ Run Evaluation ({len(_valid_rows)})", type="primary", use_container_width=True, disabled=not _valid_rows or st.session_state.batch_running):
            import time as _bt
            st.session_state.batch_results = []
            st.session_state.batch_running = True
            _total = len(_valid_rows)
            st.session_state._batch_progress = {"running": True, "done": 0, "total": _total, "current_q": ""}

            for _bi, _brow in enumerate(_valid_rows):
                _bq, _bgt = _brow["question"].strip(), _brow["ground_truth"].strip()
                st.session_state._batch_progress["current_q"] = _bq
                st.session_state._batch_progress["done"] = _bi
                
                _bts = _bt.strftime("%H:%M:%S")
                _bres = api_post("/rag/eval", {"question": _bq, "ground_truth": _bgt, "top_k": 15}, timeout=600)
                
                _res_row = {"question": _bq, "ground_truth": _bgt, "timestamp": _bts, "scores": None, "answer": "", "error": None, "tool_used": ""}
                if _bres:
                    _res_row.update({"scores": _bres.get("ragas_scores"), "answer": _bres.get("answer", ""), "error": _bres.get("ragas_error"), "tool_used": _bres.get("tool_used", "")})
                    if _res_row["scores"]:
                        st.session_state._ragas_history.append({"question": _bq, "scores": _res_row["scores"], "tool_used": _res_row["tool_used"], "timestamp": _bts})
                        st.session_state._ragas_history = st.session_state._ragas_history[-20:]
                else:
                    _res_row["error"] = "API call failed."

                st.session_state.batch_results.append(_res_row)
            
            st.session_state.batch_running = False
            st.session_state._batch_progress = {"running": False}
            st.rerun()

    if st.session_state.batch_results:
        _br = st.session_state.batch_results
        st.divider()
        st.markdown(f"**📊 Batch Results** — {len(_br)} questions")
        
        _bscored = [r for r in _br if r["scores"]]
        if _bscored:
            def _bavg(k):
                vs = [r["scores"].get(k) for r in _bscored if r["scores"].get(k) is not None]
                return round(sum(vs)/len(vs), 3) if vs else None
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Faithfulness", f"{_bavg('faithfulness') or 0:.3f}")
            c2.metric("Ans. Relevancy", f"{_bavg('answer_relevancy') or 0:.3f}")
            c3.metric("Context Precision", f"{_bavg('context_precision') or 0:.3f}")
            c4.metric("Context Recall", f"{_bavg('context_recall') or 0:.3f}")

        for _bri, _bentry in enumerate(_br):
            label = f"Q{_bri+1}: {_bentry['question'][:65]}…"
            status = "✅" if _bentry["scores"] else "❌"
            with st.expander(f"{status} {label}"):
                if _bentry["answer"]: st.markdown(f"**📄 RAG Answer:**\n{_bentry['answer']}")
                if _bentry["scores"]: _render_ragas_scores(_bentry["scores"], title=_bentry["question"])
                elif _bentry["error"]: st.error(_bentry["error"])

    history = st.session_state.get("_ragas_history", [])
    if history:
        st.divider()
        st.markdown(f"#### 📈 Session History")
        for h in reversed(history):
            with st.expander(f"**{h['question'][:70]}** · {h['timestamp']}"):
                _render_ragas_scores(h["scores"], title=h["question"])

    st.divider()
    with st.expander("ℹ️ What do these metrics mean?"):
        st.markdown("""
| Metric | What it measures | Good threshold |
|---|---|---|
| **Faithfulness** | Is every claim in the answer supported by retrieved docs? | ≥ 0.85 |
| **Answer Relevancy** | Does the answer actually address the question? | ≥ 0.80 |
| **Context Precision** | Are the retrieved chunks relevant? | ≥ 0.75 |
| **Context Recall** | Did retrieval cover all important facts? | ≥ 0.75 |
""")
