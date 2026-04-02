"""
docforge — ⚡ DocForge tab
5-step document generation wizard.
Called from streamlit_app.py via render().
"""
from ui.tabs.shared import st, httpx, api_get, api_post, API_URL, DOCX_AVAILABLE
import re


def render():

    # ── Step 1: Setup ──────────────────────────────────────────────────────────
    if st.session_state.step == 1:
        st.markdown("## ⚡ DocForge AI")
        st.caption("Enter your company details and pick a document to generate.")
        st.divider()

        if not st.session_state.departments:
            with st.spinner("Loading catalog..."):
                data = api_get("/departments")
                if data:
                    st.session_state.departments = data["departments"]

        depts = st.session_state.departments
        if not depts:
            st.warning("Backend not reachable — run: uvicorn backend.main:app --reload")
            st.stop()

        with st.container(border=True):
            st.markdown("**🏢 Company Info**")
            c1, c2 = st.columns(2)
            with c1:
                company_name = st.text_input(
                    "Company Name",
                    value=st.session_state.company_ctx.get("company_name", ""),
                    placeholder="e.g. Turabit Technologies",
                )
                industry = st.selectbox("Industry", [
                    "Technology / SaaS", "Finance / Banking", "Healthcare",
                    "Manufacturing", "Retail / E-Commerce", "Legal Services",
                    "Marketing / Media", "Logistics / Supply Chain", "Education", "Other",
                ])
            with c2:
                company_size = st.selectbox("Company Size", [
                    "1-10 employees", "11-50 employees", "51-200 employees",
                    "201-500 employees", "500+ employees",
                ], index=2)
                region = st.selectbox("Region", [
                    "India", "United States", "United Kingdom", "UAE / Middle East",
                    "Canada", "Australia", "Europe", "Other",
                ])

        with st.container(border=True):
            st.markdown("**📂 Select Document**")
            c3, c4 = st.columns(2)
            with c3:
                selected_dept = st.selectbox("Department", [d["department"] for d in depts])
            dept_data = next((d for d in depts if d["department"] == selected_dept), None)
            with c4:
                selected_doc_type = st.selectbox(
                    "Document Type",
                    dept_data["doc_types"] if dept_data else [],
                )

        st.write("")
        if st.button("Continue →", type="primary", use_container_width=True):
            if not company_name.strip():
                st.error("Please enter your company name.")
            else:
                with st.spinner("Loading sections..."):
                    safe = (selected_doc_type
                            .replace("/", "%2F")
                            .replace("(", "%28")
                            .replace(")", "%29"))
                    data = api_get(f"/sections/{safe}")
                if data:
                    st.session_state.company_ctx = {
                        "company_name": company_name.strip(),
                        "industry":     industry,
                        "company_size": company_size,
                        "region":       region,
                    }
                    st.session_state.selected_dept     = selected_dept
                    st.session_state.selected_dept_id  = dept_data["doc_id"]
                    st.session_state.selected_doc_type = selected_doc_type
                    st.session_state.doc_sec_id        = data["doc_sec_id"]
                    seen, deduped = set(), []
                    for s in data["doc_sec"]:
                        if s not in seen:
                            seen.add(s)
                            deduped.append(s)
                    st.session_state.sections          = deduped
                    st.session_state.section_questions = {}
                    st.session_state.section_answers   = {}
                    st.session_state.section_contents  = {}
                    st.session_state.full_document     = ""
                    st.session_state.gen_id            = None
                    st.session_state.docx_bytes_cache  = None
                    st.session_state._answer_drafts    = {}
                    st.session_state.step              = 2
                    st.rerun()

    # ── Step 2: Generate Questions ─────────────────────────────────────────────
    elif st.session_state.step == 2:
        sections = st.session_state.sections
        total    = len(sections)
        done     = len(st.session_state.section_questions)

        st.markdown("## ❓ Generate Questions")
        st.caption(f"{st.session_state.selected_doc_type} · {total} sections")
        st.divider()

        grid_slot    = st.empty()
        counter_slot = st.empty()

        def render_grid():
            q    = st.session_state.section_questions
            cols = st.columns(3)
            for i, s in enumerate(sections):
                mark = "✅" if s in q else "⭕"
                cols[i % 3].markdown(f"{mark}  {s[:28]}")

        def render_counter():
            d = len(st.session_state.section_questions)
            counter_slot.progress(
                d / total if total else 0,
                text=f"{d} / {total} ready",
            )

        with grid_slot.container():
            render_grid()
        render_counter()

        st.write("")
        if done < total:
            if st.button("⚡ Generate Questions for All Sections",
                         type="primary", use_container_width=True):
                status = st.empty()
                for sec in sections:
                    if sec in st.session_state.section_questions:
                        continue
                    status.caption(f"Working on: {sec}...")
                    res = api_post("/questions/generate", {
                        "doc_sec_id":      st.session_state.doc_sec_id,
                        "doc_id":          st.session_state.selected_dept_id,
                        "section_name":    sec,
                        "doc_type":        st.session_state.selected_doc_type,
                        "department":      st.session_state.selected_dept,
                        "company_context": st.session_state.company_ctx,
                    })
                    if res:
                        st.session_state.section_questions[sec] = {
                            "sec_id":       res["sec_id"],
                            "questions":    res.get("questions", []),
                            "section_type": res.get("section_type", "text"),
                        }
                    with grid_slot.container():
                        render_grid()
                    render_counter()
                status.empty()
                st.rerun()

        if done == total:
            st.success(f"✅ All {total} sections ready!")
            if st.button("Start Answering →", type="primary", use_container_width=True):
                st.session_state.step = 3
                st.rerun()

    # ── Step 3: Answer Questions ───────────────────────────────────────────────
    elif st.session_state.step == 3:
        sections   = st.session_state.sections
        ans_map    = st.session_state.section_answers
        q_map      = st.session_state.section_questions
        unanswered = [s for s in sections if s not in ans_map]

        if not unanswered:
            st.markdown("## ✅ All Sections Answered")
            st.divider()
            c1, c2 = st.columns(2)
            c1.metric("Answered", len(ans_map))
            c2.metric("Total Sections", len(sections))
            st.write("")

            if st.button("⚡ Generate Document", type="primary", use_container_width=True):
                active    = sections
                total_sec = len(active)
                progress  = st.progress(0, text="Starting...")
                ids       = []

                for i, sec in enumerate(active):
                    if sec in st.session_state.section_contents:
                        ids.append(q_map.get(sec, {}).get("sec_id", 0))
                        progress.progress(
                            (i + 1) / total_sec,
                            text=f"{i + 1}/{total_sec} done",
                        )
                        continue
                    progress.progress(
                        i / total_sec,
                        text=f"Writing: {sec}",
                    )
                    q_data = q_map.get(sec, {})
                    res = api_post("/section/generate", {
                        "sec_id":          q_data.get("sec_id"),
                        "doc_sec_id":      st.session_state.doc_sec_id,
                        "doc_id":          st.session_state.selected_dept_id,
                        "section_name":    sec,
                        "doc_type":        st.session_state.selected_doc_type,
                        "department":      st.session_state.selected_dept,
                        "company_context": st.session_state.company_ctx,
                        "num_sections":    total_sec,
                    }, timeout=120)
                    if res:
                        st.session_state.section_contents[sec] = res["content"]
                        ids.append(q_data.get("sec_id"))
                    progress.progress(
                        (i + 1) / total_sec,
                        text=f"{i + 1}/{total_sec} done",
                    )

                st.session_state.sec_ids_ordered = ids
                doc_lines = []
                for sec in active:
                    c = st.session_state.section_contents.get(sec, "").strip()
                    if c:
                        doc_lines += [sec.upper(), "-" * len(sec), "", c, "", ""]
                full_doc = "\n".join(doc_lines).strip()

                save_res = api_post("/document/save", {
                    "doc_id":          st.session_state.selected_dept_id,
                    "doc_sec_id":      st.session_state.doc_sec_id,
                    "sec_id":          ids[-1] if ids else 0,
                    "gen_doc_sec_dec": list(st.session_state.section_contents.values()),
                    "gen_doc_full":    full_doc,
                })
                st.session_state.gen_id           = save_res.get("gen_id", 0) if save_res else 0
                st.session_state.full_document    = full_doc
                st.session_state.docx_bytes_cache = None
                st.session_state.step             = 4
                st.rerun()

        else:
            current   = unanswered[0]
            done_cnt  = len(ans_map)
            total     = len(sections)
            q_data    = q_map.get(current, {})
            questions = q_data.get("questions", [])
            sec_id    = q_data.get("sec_id")
            sec_type  = q_data.get("section_type", "text")
            icon_map  = {
                "table": "📊", "flowchart": "🔀",
                "raci": "👥", "signature": "✍️", "text": "✏️",
            }
            icon = icon_map.get(sec_type, "✏️")

            st.markdown(f"## {icon}  {current}")
            st.progress(
                done_cnt / total if total else 0,
                text=f"{done_cnt} / {total} answered",
            )
            st.divider()

            if "_answer_drafts" not in st.session_state:
                st.session_state._answer_drafts = {}
            if current not in st.session_state._answer_drafts:
                st.session_state._answer_drafts[current] = [""] * len(questions)

            user_answers = []
            if not questions:
                st.info("No questions needed — this section will be auto-generated.")
            else:
                st.caption("Leave blank to auto-fill with professional content.")
                for i, q in enumerate(questions):
                    cur_val = (
                        st.session_state._answer_drafts[current][i]
                        if i < len(st.session_state._answer_drafts[current]) else ""
                    )
                    a = st.text_area(
                        f"Q{i+1}: {q}",
                        value=cur_val,
                        key=f"draft_{current}_{i}",
                        height=85,
                        placeholder="Your answer (or leave blank)...",
                    )
                    if i < len(st.session_state._answer_drafts[current]):
                        st.session_state._answer_drafts[current][i] = a
                    user_answers.append(a)

            st.write("")
            if st.button("Save & Next →", type="primary", use_container_width=True):
                filled = [a.strip() if a.strip() else "not answered" for a in user_answers]
                if sec_id:
                    api_post("/answers/save", {
                        "sec_id":       sec_id,
                        "doc_sec_id":   st.session_state.doc_sec_id,
                        "doc_id":       st.session_state.selected_dept_id,
                        "section_name": current,
                        "questions":    questions,
                        "answers":      filled or ["not answered"],
                    })
                st.session_state.section_answers[current] = filled
                st.session_state._answer_drafts.pop(current, None)
                st.rerun()

            if ans_map:
                st.divider()
                st.caption("Answered so far")
                for s in sections:
                    if s in ans_map:
                        st.markdown(f"✅ {s}")

    # ── Step 4: Review & Edit ──────────────────────────────────────────────────
    elif st.session_state.step == 4:
        active   = st.session_state.sections
        contents = st.session_state.section_contents
        icon_map = {
            "table": "📊", "flowchart": "🔀",
            "raci": "👥", "signature": "✍️", "text": "✏️",
        }

        st.markdown("## 🔍 Review & Edit")
        st.divider()

        def rebuild_doc():
            lines = []
            for sec in active:
                c = contents.get(sec, "").strip()
                if c:
                    lines += [sec.upper(), "-" * len(sec), "", c, "", ""]
            st.session_state.full_document = "\n".join(lines).strip()

        left, right = st.columns([1, 2])

        with left:
            st.caption("SECTIONS")
            sel = st.radio("", active, label_visibility="collapsed", key="sec_radio")

        with right:
            cur      = contents.get(sel, "")
            sec_type = st.session_state.section_questions.get(sel, {}).get("section_type", "text")
            icon     = icon_map.get(sec_type, "✏️")

            st.markdown(f"**{icon} {sel}**")

            with st.expander("Current Content", expanded=True):
                if cur:
                    st.text(cur)
                else:
                    st.caption("(empty)")

            st.write("")
            instr = st.text_area(
                "AI Edit Instruction",
                placeholder="e.g. Make more formal · Add detail · Shorten",
                height=60,
                key="edit_instr",
                label_visibility="collapsed",
            )
            ec1, ec2 = st.columns(2)
            with ec1:
                if st.button("🤖 Apply AI Edit", type="primary", use_container_width=True):
                    if not instr.strip():
                        st.warning("Enter an instruction.")
                    else:
                        with st.spinner("Editing..."):
                            res = api_post("/section/edit", {
                                "gen_id":           st.session_state.gen_id or 0,
                                "sec_id":           st.session_state.section_questions.get(sel, {}).get("sec_id", 0),
                                "section_name":     sel,
                                "doc_type":         st.session_state.selected_doc_type,
                                "current_content":  cur,
                                "edit_instruction": instr,
                            }, timeout=120)
                        if res:
                            st.session_state.section_contents[sel] = res["updated_content"]
                            st.session_state.docx_bytes_cache = None
                            rebuild_doc()
                            st.success("✅ Updated!")
                            st.rerun()
            with ec2:
                manual = st.text_area(
                    "Manual Edit",
                    value=cur,
                    height=180,
                    key=f"manual_{sel}",
                    label_visibility="collapsed",
                )
                if st.button("💾 Save Manual", use_container_width=True, key=f"save_{sel}"):
                    st.session_state.section_contents[sel] = manual
                    st.session_state.docx_bytes_cache = None
                    rebuild_doc()
                    st.success("✅ Saved!")
                    st.rerun()

        st.divider()
        if st.button("Export →", type="primary", use_container_width=True):
            st.session_state.step = 5
            st.rerun()

    # ── Step 5: Export ─────────────────────────────────────────────────────────
    elif st.session_state.step == 5:
        ctx      = st.session_state.company_ctx
        doc_type = st.session_state.selected_doc_type
        full_doc = st.session_state.full_document
        active   = st.session_state.sections
        contents = st.session_state.section_contents

        st.markdown("## 💾 Export")
        st.divider()

        if not full_doc:
            st.error("No document found — go back and generate first.")
            if st.button("← Back"):
                st.session_state.step = 3
                st.rerun()
            st.stop()

        st.success(f"✅ {doc_type} is ready!")

        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Document", doc_type)
            c2.metric("Department", st.session_state.selected_dept)
            c3.metric("Company", ctx.get("company_name", "--"))
            c4, c5, c6 = st.columns(3)
            c4.metric("Industry", ctx.get("industry", "--"))
            c5.metric("Sections", len(active))
            c6.metric("Words", f"~{len(full_doc.split())}")

        st.divider()
        col_n, col_d = st.columns(2)

        with col_n:
            with st.container(border=True):
                st.markdown("**📓 Publish to Notion**")
                st.caption("Send to your Notion workspace.")
                if st.button("🚀 Publish to Notion", type="primary", use_container_width=True):
                    with st.spinner("Publishing..."):
                        res = api_post("/document/publish", {
                            "gen_id":          st.session_state.gen_id or 0,
                            "doc_type":        doc_type,
                            "department":      st.session_state.selected_dept,
                            "gen_doc_full":    full_doc,
                            "company_context": ctx,
                        })
                    if res:
                        url = res.get("notion_url", "")
                        st.success("✅ Published!")
                        if url:
                            st.link_button("🔗 Open in Notion", url, use_container_width=True)

        with col_d:
            with st.container(border=True):
                st.markdown("**📥 Download**")
                safe = (doc_type
                        .replace(" ", "_")
                        .replace("/", "-")
                        .replace("(", "")
                        .replace(")", ""))

                if DOCX_AVAILABLE:
                    if (st.session_state.get("docx_bytes_cache") is None
                            or st.session_state.get("docx_cache_doc") != doc_type):
                        try:
                            sections_data = [
                                {"name": sec, "content": contents.get(sec, "")}
                                for sec in active if contents.get(sec)
                            ]
                            st.session_state.docx_bytes_cache = build_docx(
                                doc_type=doc_type,
                                department=st.session_state.selected_dept,
                                company_name=ctx.get("company_name", "Company"),
                                industry=ctx.get("industry", ""),
                                region=ctx.get("region", ""),
                                sections=sections_data,
                            )
                            st.session_state.docx_cache_doc = doc_type
                        except Exception as e:
                            st.error(f"DOCX error: {e}")
                            st.session_state.docx_bytes_cache = None

                    if st.session_state.get("docx_bytes_cache"):
                        st.download_button(
                            "⬇️ Download .docx",
                            data=st.session_state.docx_bytes_cache,
                            file_name=f"{safe}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            type="primary",
                        )
                else:
                    st.warning("docx_builder.py not found.")

                st.download_button(
                    "⬇️ Download .txt",
                    data=full_doc,
                    file_name=f"{safe}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

        st.divider()
        with st.expander("📄 Preview Full Document"):
            st.text(full_doc)

        st.write("")
        if st.button("➕ Create Another Document", type="primary", use_container_width=True):
            saved_ctx   = st.session_state.company_ctx
            saved_depts = st.session_state.departments
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            init_session()
            st.session_state["company_ctx"]  = saved_ctx
            st.session_state["departments"]  = saved_depts
            st.session_state["step"]         = 1
            st.rerun()

