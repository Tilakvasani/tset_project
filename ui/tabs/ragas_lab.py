"""
ragas_lab — 📊 RAGAS Evaluation tab
Manual evaluation runs, score history, per-metric breakdowns.
Called from streamlit_app.py via render().
"""
from ui.tabs.shared import st, httpx, api_get, api_post, API_URL, DOCX_AVAILABLE
import io, datetime

try:
    from docx_builder import build_docx
    _DOCX_OK = True
except ImportError:
    _DOCX_OK = False


def _build_ragas_report(history: list, last_scores: dict | None) -> bytes:
    """
    Build a professional RAGAS evaluation report as a .docx file.
    Uses docx_builder.build_docx so it matches the rest of the project style.
    """
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def _score_line(label, val):
        if val is None:
            return f"{label}: N/A"
        pct = f"{val:.2%}"
        tag = "✅" if val >= 0.85 else "⚠️" if val >= 0.70 else "❌"
        return f"{tag}  {label}: {pct}"

    def _scores_to_text(scores: dict) -> str:
        lines = [
            _score_line("Faithfulness",      scores.get("faithfulness")),
            _score_line("Answer Relevancy",  scores.get("answer_relevancy")),
            _score_line("Context Precision", scores.get("context_precision")),
            _score_line("Context Recall",    scores.get("context_recall")),
        ]
        vals = [v for v in scores.values() if v is not None]
        if vals:
            avg = sum(vals) / len(vals)
            lines.append(f"\nOverall Average: {avg:.2%}")
        return "\n".join(lines)

    sections = []

    # ── Section 1: Summary ──────────────────────────────────────────────────
    summary_lines = [f"Report generated: {now_str}"]
    if last_scores:
        summary_lines.append("\nLatest evaluation scores:")
        summary_lines.append(_scores_to_text(last_scores))
    if history:
        vals_f = [h["scores"].get("faithfulness")      for h in history if h.get("scores") and h["scores"].get("faithfulness")      is not None]
        vals_r = [h["scores"].get("answer_relevancy")  for h in history if h.get("scores") and h["scores"].get("answer_relevancy")  is not None]
        vals_p = [h["scores"].get("context_precision") for h in history if h.get("scores") and h["scores"].get("context_precision") is not None]
        vals_c = [h["scores"].get("context_recall")    for h in history if h.get("scores") and h["scores"].get("context_recall")    is not None]
        summary_lines.append(f"\nSession totals: {len(history)} evaluations scored")
        if vals_f: summary_lines.append(f"• Avg Faithfulness:      {sum(vals_f)/len(vals_f):.2%}")
        if vals_r: summary_lines.append(f"• Avg Answer Relevancy:  {sum(vals_r)/len(vals_r):.2%}")
        if vals_p: summary_lines.append(f"• Avg Context Precision: {sum(vals_p)/len(vals_p):.2%}")
        if vals_c: summary_lines.append(f"• Avg Context Recall:    {sum(vals_c)/len(vals_c):.2%}")
    sections.append({"name": "Evaluation Summary", "content": "\n".join(summary_lines)})

    # ── Section 2: Per-question results ─────────────────────────────────────
    if history:
        rows = ["| # | Question | Faithfulness | Relevancy | Precision | Recall |",
                "|---|---|---|---|---|---|"]
        for i, entry in enumerate(reversed(history), 1):
            sc = entry.get("scores") or {}
            q  = entry.get("question", "")[:80]
            f_ = f"{sc.get('faithfulness', 0):.2f}"      if sc.get("faithfulness")      is not None else "—"
            r_ = f"{sc.get('answer_relevancy', 0):.2f}"  if sc.get("answer_relevancy")  is not None else "—"
            p_ = f"{sc.get('context_precision', 0):.2f}" if sc.get("context_precision") is not None else "—"
            c_ = f"{sc.get('context_recall', 0):.2f}"    if sc.get("context_recall")    is not None else "—"
            rows.append(f"| {i} | {q} | {f_} | {r_} | {p_} | {c_} |")
        sections.append({"name": "Question-Level Results", "content": "\n".join(rows)})

        # ── Section 3: Detailed breakdown ───────────────────────────────────
        detail_lines = []
        for i, entry in enumerate(reversed(history), 1):
            sc = entry.get("scores") or {}
            if not sc:
                continue
            detail_lines.append(f"{i}. {entry.get('question', 'N/A')}")
            detail_lines.append(_scores_to_text(sc))
            if entry.get("timestamp"):
                detail_lines.append(f"   Evaluated: {entry['timestamp']}")
            detail_lines.append("")
        if detail_lines:
            sections.append({"name": "Detailed Breakdown", "content": "\n".join(detail_lines)})

    # ── Section 4: Metric reference ─────────────────────────────────────────
    ref = (
        "| Metric | What it measures | Target |\n"
        "|---|---|---|\n"
        "| Faithfulness | Every claim is grounded in retrieved docs — no hallucination | ≥ 0.85 |\n"
        "| Answer Relevancy | Answer directly addresses the question asked | ≥ 0.80 |\n"
        "| Context Precision | Retrieved chunks are relevant — low noise | ≥ 0.75 |\n"
        "| Context Recall | Retrieval covered all important facts (needs ground truth) | ≥ 0.75 |"
    )
    sections.append({"name": "Metric Reference", "content": ref})

    return build_docx(
        doc_type="RAGAS Evaluation Report",
        department="AI Quality",
        company_name="DocForge AI",
        industry="Technology / SaaS",
        region="",
        sections=sections,
    )


def render():

    st.markdown("""
    <div style="padding:0 0 1rem">
    <h2 style="color:#e2e8f0;font-weight:700;margin-bottom:0.25rem">📊 RAGAS Evaluation</h2>
    <p style="color:#475569;font-size:0.9rem">Real answer quality scores — faithfulness, relevancy, precision, recall</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

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

            def _handle_json_upload():
                uploaded = st.session_state.get("batch_json_upload")
                if uploaded:
                    import json as _json
                    try:
                        raw_data = _json.loads(uploaded.read().decode("utf-8"))
                        if not isinstance(raw_data, list):
                            st.session_state["_batch_err"] = "JSON must be a list of objects."
                        else:
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
                                st.session_state["_batch_succ"] = f"Loaded {len(parsed_rows)} questions from JSON."
                            else:
                                st.session_state["_batch_err"] = "No valid questions found in JSON."
                    except Exception as _je:
                        st.session_state["_batch_err"] = f"JSON parse error: {_je}"

            st.file_uploader(
                "Upload JSON file",
                type=["json"],
                key="batch_json_upload",
                label_visibility="collapsed",
                on_change=_handle_json_upload,
            )

            if "_batch_succ" in st.session_state:
                st.success(st.session_state.pop("_batch_succ"))
            if "_batch_err" in st.session_state:
                st.error(st.session_state.pop("_batch_err"))

        # ── Manual rows ────────────────────────────────────────────────────────
        st.markdown("**Questions**")
        rows_to_delete = []
        for _ri, _row in enumerate(st.session_state.batch_rows):
            _rc1, _rc2, _rc3 = st.columns([3, 3, 0.5])
            with _rc1:
                _q_val = st.text_input(
                    f"Question {_ri + 1}",
                    value=_row["question"],
                    placeholder="e.g. What is the leave policy?",
                    key=f"batch_q_{_ri}",
                    label_visibility="collapsed",
                )
                st.session_state.batch_rows[_ri]["question"] = _q_val
            with _rc2:
                _gt_val = st.text_input(
                    f"Ground Truth {_ri + 1}",
                    value=_row["ground_truth"],
                    placeholder="Ground truth",
                    key=f"batch_gt_{_ri}",
                    label_visibility="collapsed",
                )
                st.session_state.batch_rows[_ri]["ground_truth"] = _gt_val
            with _rc3:
                if len(st.session_state.batch_rows) > 1:
                    if st.button("✕", key=f"batch_del_{_ri}", help="Remove row"):
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
            st.caption(f"{len(st.session_state.batch_rows)} question(s) queued · Each takes 20–60s · No timeout limit")

        st.write("")
        _valid_rows = [r for r in st.session_state.batch_rows if r["question"].strip() and r['ground_truth'].strip()]

        # ── Live progress display (survives st.rerun) ─────────────────────────
        _bp = st.session_state.get("_batch_progress")
        if _bp and _bp.get("running"):
            _done  = _bp["done"]
            _total = _bp["total"]
            _frac  = _done / _total if _total else 0
            st.progress(_frac, text=f"⏳ Running {_done}/{_total}: {_bp.get('current_q', '')[:55]}…")
            st.caption(f"Question {_done} of {_total} complete — waiting for next result…")

        if st.button(
            f"▶ Run Batch ({len(_valid_rows)} questions)",
            type="primary",
            key="batch_run_btn",
            use_container_width=True,
            disabled=len(_valid_rows) == 0 or st.session_state.get("batch_running", False),
        ):
            if _valid_rows:
                import time as _bt
                st.session_state.batch_results = []
                st.session_state.batch_running = True
                _total = len(_valid_rows)
                st.session_state._batch_progress = {
                    "running": True, "done": 0, "total": _total, "current_q": ""
                }

                for _bi, _brow in enumerate(_valid_rows):
                    _bq  = _brow["question"].strip()
                    _bgt = _brow["ground_truth"].strip()

                    # Update progress state so the re-render above shows current status
                    st.session_state._batch_progress["current_q"] = _bq
                    st.session_state._batch_progress["done"]       = _bi

                    _bts  = _bt.strftime("%H:%M:%S")
                    _bres = api_post("/rag/eval", {
                        "question":     _bq,
                        "ground_truth": _bgt,
                        "top_k":        15,
                    }, timeout=600)

                    _bresult = {
                        "question":     _bq,
                        "ground_truth": _bgt,
                        "timestamp":    _bts,
                        "scores":       None,
                        "answer":       "",
                        "error":        None,
                        "tool_used":    "",
                    }
                    if _bres:
                        _bresult["scores"]    = _bres.get("ragas_scores")
                        _bresult["answer"]    = _bres.get("answer", "")
                        _bresult["error"]     = _bres.get("ragas_error")
                        _bresult["tool_used"] = _bres.get("tool_used", "")
                        if _bresult["scores"]:
                            st.session_state._ragas_history.append({
                                "question":  _bq,
                                "scores":    _bresult["scores"],
                                "tool_used": _bresult["tool_used"],
                                "timestamp": _bts,
                            })
                            st.session_state._ragas_history = st.session_state._ragas_history[-20:]
                    else:
                        _bresult["error"] = "API call failed — backend unreachable."

                    st.session_state.batch_results.append(_bresult)
                    st.session_state._batch_progress["done"] = _bi + 1

                st.session_state._batch_progress = {"running": False, "done": _total, "total": _total, "current_q": ""}
                st.session_state.batch_running = False
                st.rerun()

    # ── Batch results display ─────────────────────────────────────────────────
    if st.session_state.batch_results:
        _br = st.session_state.batch_results
        st.divider()
        st.markdown(f"**📊 Batch Results** — {len(_br)} questions")

        # Aggregate summary row
        _bscored = [r for r in _br if r["scores"]]
        if _bscored:
            def _bavg(key):
                vals = [r["scores"].get(key) for r in _bscored if r["scores"].get(key) is not None]
                return round(sum(vals) / len(vals), 3) if vals else None

            _bfa = _bavg("faithfulness")
            _bra = _bavg("answer_relevancy")
            _bpa = _bavg("context_precision")
            _bca = _bavg("context_recall")

            with st.container(border=True):
                st.caption(f"BATCH AVERAGES · {len(_bscored)}/{len(_br)} scored")
                _bc1, _bc2, _bc3, _bc4 = st.columns(4)
                def _bm(col, label, val):
                    if val is not None:
                        col.metric(label, f"{val:.3f}")
                    else:
                        col.metric(label, "n/a")
                _bm(_bc1, "Faithfulness",      _bfa)
                _bm(_bc2, "Ans. Relevancy",     _bra)
                _bm(_bc3, "Context Precision",  _bpa)
                _bm(_bc4, "Context Recall",     _bca)

        # Per-question expandable cards
        for _bri, _bentry in enumerate(_br):
            _blabel = f"Q{_bri+1}: {_bentry['question'][:65]}{'…' if len(_bentry['question']) > 65 else ''}"
            _bstatus = "✅" if _bentry["scores"] else ("❌" if _bentry["error"] else "⚠️")
            with st.expander(f"{_bstatus} {_blabel} · {_bentry['timestamp']}"):
                if _bentry["answer"]:
                    st.markdown(f"**📄 RAG Answer:**")
                    st.markdown(_bentry["answer"])
                if _bentry["scores"]:
                    _render_ragas_scores(_bentry["scores"], title=_bentry["question"])
                elif _bentry["error"]:
                    st.error(f"RAGAS error: {_bentry['error']}")
                else:
                    st.warning("No scores returned — check backend logs.")

        # Export batch results as JSON
        import json as _ejson, time as _et
        _export_data = [
            {
                "question":     r["question"],
                "ground_truth": r["ground_truth"],
                "timestamp":    r["timestamp"],
                "tool_used":    r["tool_used"],
                "answer":       r["answer"],
                "scores":       r["scores"],
                "error":        r["error"],
            }
            for r in _br
        ]
        st.download_button(
            "⬇️ Export Results as JSON",
            data=_ejson.dumps(_export_data, indent=2),
            file_name=f"ragas_batch_{_et.strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            key="batch_export_btn",
        )

    # ── Section 4: Session history ────────────────────────────────────────────

    history = st.session_state.get("_ragas_history", [])
    if history:
        st.divider()
        st.markdown(f"#### 📈 Session History  <span style=\'font-size:12px;color:#475569;font-weight:400\'>{len(history)} evaluations</span>", unsafe_allow_html=True)

        # Aggregate trend
        all_faith  = [h["scores"].get("faithfulness")      for h in history if h["scores"].get("faithfulness")      is not None]
        all_relev  = [h["scores"].get("answer_relevancy")  for h in history if h["scores"].get("answer_relevancy")  is not None]
        all_prec   = [h["scores"].get("context_precision") for h in history if h["scores"].get("context_precision") is not None]
        all_rec    = [h["scores"].get("context_recall")    for h in history if h["scores"].get("context_recall")    is not None]

        def _avg(lst):
            return round(sum(lst) / len(lst), 2) if lst else None

        fa, ra, pa, ca = _avg(all_faith), _avg(all_relev), _avg(all_prec), _avg(all_rec)

        c1, c2, c3, c4 = st.columns(4)
        def _metric_col(col, label, val):
            if val is not None:
                col.metric(label, f"{val:.2f}", delta=None)
            else:
                col.metric(label, "n/a")

        _metric_col(c1, "Avg Faithfulness",      fa)
        _metric_col(c2, "Avg Ans. Relevancy",     ra)
        _metric_col(c3, "Avg Context Precision",  pa)
        _metric_col(c4, "Avg Context Recall",     ca)

        st.write("")

        for entry in reversed(history):
            q_label  = entry["question"][:70] + ("…" if len(entry["question"]) > 70 else "")
            tool_tag = f" · `{entry['tool_used']}`" if entry.get("tool_used") else ""
            ts_tag   = f" · {entry['timestamp']}" if entry.get("timestamp") else ""
            with st.expander(f"**{q_label}**{tool_tag}{ts_tag}"):
                _render_ragas_scores(entry["scores"], title=entry["question"])

        # ── Download Report button ─────────────────────────────────────────
        st.write("")
        _rc1, _rc2 = st.columns([1, 1])
        with _rc1:
            if _DOCX_OK:
                try:
                    _report_bytes = _build_ragas_report(
                        history,
                        st.session_state.get("_last_ragas_scores"),
                    )
                    _fname = f"RAGAS_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.docx"
                    st.download_button(
                        label="📥 Download Report (.docx)",
                        data=_report_bytes,
                        file_name=_fname,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        key="ragas_download_report",
                    )
                except Exception as _re:
                    st.warning(f"Report generation failed: {_re}")
            else:
                st.button(
                    "📥 Download Report (.docx)",
                    disabled=True,
                    use_container_width=True,
                    help="Install python-docx to enable: pip install python-docx",
                    key="ragas_download_report_disabled",
                )
        with _rc2:
            if st.button("🗑 Clear History", key="ragas_clear_hist", use_container_width=True):
                st.session_state._ragas_history = []
                st.rerun()

    # ── Section 4: Metric explanations ────────────────────────────────────────
    st.divider()
    with st.expander("ℹ️ What do these metrics mean?"):
        st.markdown("""
    | Metric | What it measures | Good threshold |
    |---|---|---|
    | **Faithfulness** | Is every claim in the answer supported by the retrieved documents? High = no hallucination. | ≥ 0.85 |
    | **Answer Relevancy** | Does the answer actually address the question? Low = answer went off-topic. | ≥ 0.80 |
    | **Context Precision** | Are the retrieved chunks relevant? Low = retriever is pulling in noise. | ≥ 0.75 |
    | **Context Recall** | Did retrieval cover all the important facts? Only scored when a **Ground Truth** is provided in the batch or eval form. | ≥ 0.75 |
    """)
