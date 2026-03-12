"""
DocForge AI — streamlit_app.py
Full workflow UI:
  Step 1: Company Context
  Step 2: Select Department → Doc Type
  Step 3: Generate Questions (LLM) per section
  Step 4: User answers questions
  Step 5: Generate section content (LLM)
  Step 6: Combine → Full document
  Step 7: Review → Edit/Enhance sections
  Step 8: Save → Publish / Download
"""
import sys
import os

# ── Path fix ──────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import httpx
import json

API_URL = "http://localhost:8000/api"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocForge AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .step-badge {
        background: #667eea;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }
    .section-card {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: #f8fafc;
    }
    .success-box {
        background: #f0fdf4;
        border: 1px solid #86efac;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .progress-step {
        display: inline-block;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        text-align: center;
        line-height: 32px;
        font-weight: bold;
        margin-right: 8px;
    }
    .step-active { background: #667eea; color: white; }
    .step-done { background: #22c55e; color: white; }
    .step-pending { background: #e2e8f0; color: #94a3b8; }
</style>
""", unsafe_allow_html=True)


# ─── API Helpers ──────────────────────────────────────────────────────────────

def api_get(endpoint: str):
    try:
        r = httpx.get(f"{API_URL}{endpoint}", timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def api_post(endpoint: str, data: dict, timeout: int = 120):
    try:
        r = httpx.post(f"{API_URL}{endpoint}", json=data, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# ─── Session State Init ───────────────────────────────────────────────────────

def init_session():
    defaults = {
        "step": 1,
        "company_ctx": {},
        "departments": [],
        "selected_dept": None,
        "selected_dept_id": None,
        "selected_doc_type": None,
        "doc_sec_id": None,
        "sections": [],
        "current_section_idx": 0,
        "section_questions": {},   # sec_name → {sec_id, questions}
        "section_answers": {},     # sec_name → [answers]
        "section_contents": {},    # sec_name → content string
        "sec_ids_ordered": [],     # ordered list of sec_ids
        "gen_id": None,
        "full_document": "",
        "edit_mode": False,
        "edit_section_name": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ─── Sidebar: Progress Tracker ────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("## 📄 DocForge AI")
        st.markdown("---")

        steps = [
            (1, "Company Context"),
            (2, "Select Document"),
            (3, "Generate Questions"),
            (4, "Answer Questions"),
            (5, "Generate Sections"),
            (6, "Full Document"),
            (7, "Review & Edit"),
            (8, "Save & Export"),
        ]

        current = st.session_state.step

        for num, label in steps:
            if num < current:
                icon = "✅"
                color = "#22c55e"
            elif num == current:
                icon = "▶️"
                color = "#667eea"
            else:
                icon = "⭕"
                color = "#94a3b8"

            st.markdown(
                f'<div style="color:{color}; padding:4px 0; font-weight:{"600" if num==current else "400"}">'
                f'{icon} Step {num}: {label}</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")

        if st.session_state.company_ctx:
            ctx = st.session_state.company_ctx
            st.markdown("**Company**")
            st.caption(ctx.get("company_name", "—"))
            st.caption(f"{ctx.get('industry', '—')} · {ctx.get('region', '—')}")

        if st.session_state.selected_doc_type:
            st.markdown("**Document**")
            st.caption(st.session_state.selected_doc_type)

        if st.session_state.sections:
            done = len(st.session_state.section_contents)
            total = len(st.session_state.sections)
            st.markdown(f"**Sections: {done}/{total}**")
            st.progress(done / total if total else 0)

        st.markdown("---")
        if st.button("🔄 Start Over", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


render_sidebar()


# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>📄 DocForge AI</h1>
    <p style="margin:0; opacity:0.9">AI-Powered Enterprise Document Generator</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 1: Company Context
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.step == 1:
    st.markdown('<span class="step-badge">Step 1 of 8</span>', unsafe_allow_html=True)
    st.markdown("## 🏢 Company Context")
    st.markdown("Tell us about your company so we can generate relevant, specific questions.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        company_name = st.text_input(
            "Company Name *",
            value=st.session_state.company_ctx.get("company_name", ""),
            placeholder="e.g. Turabit Technologies"
        )
        industry = st.selectbox(
            "Industry *",
            ["Technology / SaaS", "Finance / Banking", "Healthcare", "Manufacturing",
             "Retail / E-Commerce", "Legal Services", "Marketing / Media",
             "Logistics / Supply Chain", "Education", "Other"],
            index=0
        )

    with col2:
        company_size = st.selectbox(
            "Company Size",
            ["1–10 employees", "11–50 employees", "51–200 employees",
             "201–500 employees", "500+ employees"],
            index=2
        )
        region = st.selectbox(
            "Region / Country",
            ["India", "United States", "United Kingdom", "UAE / Middle East",
             "Canada", "Australia", "Europe", "Other"],
            index=0
        )

    st.markdown("---")

    if st.button("Continue →", type="primary", use_container_width=True):
        if not company_name.strip():
            st.error("Please enter your company name.")
        else:
            st.session_state.company_ctx = {
                "company_name": company_name.strip(),
                "industry": industry,
                "company_size": company_size,
                "region": region
            }
            st.session_state.step = 2
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 2: Select Department & Document Type
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.step == 2:
    st.markdown('<span class="step-badge">Step 2 of 8</span>', unsafe_allow_html=True)
    st.markdown("## 📂 Select Document")
    st.markdown("---")

    # Load departments from DB
    if not st.session_state.departments:
        with st.spinner("Loading departments..."):
            data = api_get("/departments")
            if data:
                st.session_state.departments = data["departments"]

    departments = st.session_state.departments

    if not departments:
        st.error("Could not load departments. Make sure the backend is running.")
        st.stop()

    dept_names = [d["department"] for d in departments]

    col1, col2 = st.columns(2)
    with col1:
        selected_dept = st.selectbox("Department", dept_names)

    # Get doc types for selected dept
    dept_data = next((d for d in departments if d["department"] == selected_dept), None)
    doc_types = dept_data["doc_types"] if dept_data else []

    with col2:
        selected_doc_type = st.selectbox("Document Type", doc_types)

    if selected_doc_type:
        st.markdown("---")
        st.markdown(f"**Selected:** `{selected_dept}` → `{selected_doc_type}`")

    st.markdown("---")

    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("← Back"):
            st.session_state.step = 1
            st.rerun()
    with col_next:
        if st.button("Load Sections →", type="primary", use_container_width=True):
            with st.spinner("Loading document sections..."):
                encoded = selected_doc_type.replace("/", "%2F")
                data = api_get(f"/sections/{encoded}")
                if data:
                    st.session_state.selected_dept = selected_dept
                    st.session_state.selected_dept_id = dept_data["doc_id"]
                    st.session_state.selected_doc_type = selected_doc_type
                    st.session_state.doc_sec_id = data["doc_sec_id"]
                    st.session_state.sections = data["doc_sec"]
                    st.session_state.step = 3
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 3: Generate Questions (LLM) — Section by Section
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.step == 3:
    st.markdown('<span class="step-badge">Step 3 of 8</span>', unsafe_allow_html=True)
    st.markdown(f"## ❓ Generate Questions — {st.session_state.selected_doc_type}")
    st.markdown(f"**{len(st.session_state.sections)} sections** to process")
    st.markdown("---")

    sections = st.session_state.sections
    generated = st.session_state.section_questions

    # Show section status
    cols = st.columns(4)
    for i, sec in enumerate(sections):
        done = sec in generated
        cols[i % 4].markdown(
            f'<div style="padding:4px; font-size:12px; color:{"#22c55e" if done else "#94a3b8"}">'
            f'{"✅" if done else "⭕"} {sec[:30]}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    total = len(sections)
    done_count = len(generated)

    st.progress(done_count / total)
    st.markdown(f"**{done_count} / {total} sections have questions generated**")

    # Generate all at once
    if done_count < total:
        if st.button("🤖 Generate Questions for All Sections", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status = st.empty()

            for i, section_name in enumerate(sections):
                if section_name in generated:
                    continue

                status.markdown(f"⏳ Generating questions for: **{section_name}**...")

                result = api_post("/questions/generate", {
                    "doc_sec_id": st.session_state.doc_sec_id,
                    "doc_id": st.session_state.selected_dept_id,
                    "section_name": section_name,
                    "doc_type": st.session_state.selected_doc_type,
                    "department": st.session_state.selected_dept,
                    "company_context": st.session_state.company_ctx
                })

                if result:
                    st.session_state.section_questions[section_name] = {
                        "sec_id": result["sec_id"],
                        "questions": result["questions"]
                    }

                progress_bar.progress((i + 1) / total)

            status.markdown("✅ **All questions generated!**")
            st.rerun()

    # Show generated questions preview
    if generated:
        with st.expander("📋 Preview Generated Questions", expanded=False):
            for sec_name, q_data in list(generated.items())[:3]:
                st.markdown(f"**{sec_name}**")
                for q in q_data["questions"]:
                    st.markdown(f"- {q}")
                st.markdown("---")

    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("← Back"):
            st.session_state.step = 2
            st.rerun()
    with col_next:
        if done_count == total:
            if st.button("Answer Questions →", type="primary", use_container_width=True):
                st.session_state.step = 4
                st.session_state.current_section_idx = 0
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 4: User Answers Questions — Section by Section
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.step == 4:
    sections = st.session_state.sections
    answers_map = st.session_state.section_answers
    questions_map = st.session_state.section_questions
    current_idx = st.session_state.current_section_idx

    # Find next unanswered section
    unanswered = [s for s in sections if s not in answers_map]

    if not unanswered:
        st.success("✅ All sections answered!")
        if st.button("Generate Section Content →", type="primary"):
            st.session_state.step = 5
            st.rerun()
    else:
        current_section = unanswered[0]
        done_count = len(answers_map)
        total = len(sections)

        st.markdown('<span class="step-badge">Step 4 of 8</span>', unsafe_allow_html=True)
        st.markdown(f"## ✍️ Answer Questions")
        st.markdown(f"**Section {done_count + 1} of {total}: {current_section}**")

        st.progress(done_count / total)
        st.markdown("---")

        q_data = questions_map.get(current_section, {})
        questions = q_data.get("questions", [])
        sec_id = q_data.get("sec_id")

        st.markdown(f"### 📌 {current_section}")
        st.markdown("*Answer these questions to generate rich content for this section:*")

        user_answers = []
        for i, question in enumerate(questions):
            ans = st.text_area(
                f"Q{i+1}: {question}",
                key=f"ans_{current_section}_{i}",
                height=80,
                placeholder="Enter your answer here..."
            )
            user_answers.append(ans)

        st.markdown("---")

        col_skip, col_save = st.columns([1, 3])

        with col_skip:
            if st.button("Skip Section"):
                # Save blank answers and move on
                blank = ["Not provided"] * len(questions)
                api_post("/answers/save", {
                    "sec_id": sec_id,
                    "doc_sec_id": st.session_state.doc_sec_id,
                    "doc_id": st.session_state.selected_dept_id,
                    "section_name": current_section,
                    "questions": questions,
                    "answers": blank
                })
                st.session_state.section_answers[current_section] = blank
                st.rerun()

        with col_save:
            if st.button("Save & Next Section →", type="primary", use_container_width=True):
                filled = [a.strip() if a.strip() else "Not provided" for a in user_answers]

                with st.spinner("Saving answers..."):
                    result = api_post("/answers/save", {
                        "sec_id": sec_id,
                        "doc_sec_id": st.session_state.doc_sec_id,
                        "doc_id": st.session_state.selected_dept_id,
                        "section_name": current_section,
                        "questions": questions,
                        "answers": filled
                    })

                if result:
                    st.session_state.section_answers[current_section] = filled
                    st.rerun()

        # Show answered sections
        if answers_map:
            st.markdown("---")
            st.markdown("**Completed sections:**")
            for sec in sections:
                if sec in answers_map:
                    st.markdown(f"✅ {sec}")


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 5: Generate Section Content (LLM)
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.step == 5:
    st.markdown('<span class="step-badge">Step 5 of 8</span>', unsafe_allow_html=True)
    st.markdown(f"## ⚙️ Generate Section Content")
    st.markdown(f"**{st.session_state.selected_doc_type}** — LLM writes each section using your answers")
    st.markdown("---")

    sections = st.session_state.sections
    questions_map = st.session_state.section_questions
    contents = st.session_state.section_contents
    total = len(sections)
    done_count = len(contents)

    st.progress(done_count / total)
    st.markdown(f"**{done_count} / {total} sections generated**")

    if done_count < total:
        if st.button("🤖 Generate All Sections", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status = st.empty()
            sec_ids_ordered = []

            for i, section_name in enumerate(sections):
                if section_name in contents:
                    sec_ids_ordered.append(questions_map[section_name]["sec_id"])
                    continue

                status.markdown(f"✍️ Writing: **{section_name}**...")

                q_data = questions_map.get(section_name, {})
                sec_id = q_data.get("sec_id")

                result = api_post("/section/generate", {
                    "sec_id": sec_id,
                    "doc_sec_id": st.session_state.doc_sec_id,
                    "doc_id": st.session_state.selected_dept_id,
                    "section_name": section_name,
                    "doc_type": st.session_state.selected_doc_type,
                    "department": st.session_state.selected_dept,
                    "company_context": st.session_state.company_ctx
                }, timeout=120)

                if result:
                    st.session_state.section_contents[section_name] = result["content"]
                    sec_ids_ordered.append(sec_id)

                progress_bar.progress((i + 1) / total)

            st.session_state.sec_ids_ordered = sec_ids_ordered
            status.markdown("✅ **All sections generated!**")
            st.rerun()

    # Preview
    if contents:
        with st.expander("👁️ Preview Generated Sections", expanded=False):
            for sec_name, content in list(contents.items())[:2]:
                st.markdown(f"**{sec_name}**")
                st.markdown(content[:300] + "...")
                st.markdown("---")

    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("← Back"):
            st.session_state.step = 4
            st.rerun()
    with col_next:
        if done_count == total:
            if st.button("Assemble Full Document →", type="primary", use_container_width=True):
                st.session_state.step = 6
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 6: Combine Sections → Full Document
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.step == 6:
    st.markdown('<span class="step-badge">Step 6 of 8</span>', unsafe_allow_html=True)
    st.markdown("## 📄 Assemble Full Document")
    st.markdown("---")

    if not st.session_state.full_document:
        st.info("Click below to assemble all sections into the complete document and run the final polish pass.")

        if st.button("🔧 Assemble & Polish Document", type="primary", use_container_width=True):
            with st.spinner("Assembling and polishing document via LLM..."):

                # Build combined sections locally first to pass content
                sections = st.session_state.sections
                contents = st.session_state.section_contents
                questions_map = st.session_state.section_questions

                # Inject generated_content into Q&A JSONB so combine_document can use it
                for sec_name, content in contents.items():
                    q_data = questions_map.get(sec_name, {})
                    sec_id = q_data.get("sec_id")
                    if sec_id:
                        # Patch Q&A with generated content for the combine step
                        api_post("/answers/save", {
                            "sec_id": sec_id,
                            "doc_sec_id": st.session_state.doc_sec_id,
                            "doc_id": st.session_state.selected_dept_id,
                            "section_name": sec_name,
                            "questions": q_data.get("questions", []),
                            "answers": st.session_state.section_answers.get(sec_name, []),
                            "generated_content": content  # extra field
                        })

                # Build full doc locally
                ctx = st.session_state.company_ctx
                header = f"""# {st.session_state.selected_doc_type}

**Organization:** {ctx.get('company_name', 'Company')}
**Department:** {st.session_state.selected_dept}
**Industry:** {ctx.get('industry', 'N/A')}
**Region:** {ctx.get('region', 'N/A')}
**Document Version:** v1.0
**Classification:** Internal Use Only
**Generated by:** DocForge AI

---

"""
                body_parts = []
                for sec_name in sections:
                    content = contents.get(sec_name, "")
                    if content:
                        body_parts.append(f"## {sec_name}\n\n{content}")

                full_draft = header + "\n\n---\n\n".join(body_parts)

                # Save to gen_doc via combine endpoint
                result = api_post("/document/combine", {
                    "doc_id": st.session_state.selected_dept_id,
                    "doc_sec_id": st.session_state.doc_sec_id,
                    "doc_type": st.session_state.selected_doc_type,
                    "department": st.session_state.selected_dept,
                    "sec_ids": st.session_state.sec_ids_ordered,
                    "company_context": st.session_state.company_ctx
                }, timeout=180)

                if result:
                    st.session_state.gen_id = result["gen_id"]
                    # Use locally built full_draft if LLM combine returns empty
                    final = result.get("gen_doc_full") or full_draft
                    st.session_state.full_document = final
                else:
                    # Fallback: use local assembly
                    st.session_state.full_document = full_draft
                    st.session_state.gen_id = 0

            st.rerun()

    else:
        st.success(f"✅ Document assembled! **gen_id: {st.session_state.gen_id}**")
        st.markdown("---")

        # Show document
        with st.expander("📄 View Full Document", expanded=True):
            st.markdown(st.session_state.full_document)

        st.markdown("---")
        col_back, col_next = st.columns([1, 3])
        with col_back:
            if st.button("← Back"):
                st.session_state.step = 5
                st.rerun()
        with col_next:
            if st.button("Review & Edit →", type="primary", use_container_width=True):
                st.session_state.step = 7
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 7: Review & Edit
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.step == 7:
    st.markdown('<span class="step-badge">Step 7 of 8</span>', unsafe_allow_html=True)
    st.markdown("## 🔍 Review & Edit")
    st.markdown("---")

    sections = st.session_state.sections
    contents = st.session_state.section_contents

    # Left: section list | Right: document preview
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("### 📋 Sections")
        selected_edit_section = st.radio(
            "Select a section to edit:",
            sections,
            label_visibility="collapsed"
        )

    with col_right:
        st.markdown(f"### ✏️ Editing: {selected_edit_section}")

        current_content = contents.get(selected_edit_section, "")
        st.markdown("**Current Content:**")
        st.markdown(current_content)

        st.markdown("---")
        st.markdown("**🤖 AI Edit / Enhance**")

        edit_instruction = st.text_area(
            "Edit instruction",
            placeholder="e.g. Make it more formal, Add more details about compensation structure, Shorten this section...",
            height=80,
            key="edit_instruction_input"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🤖 Apply AI Edit", type="primary", use_container_width=True):
                if not edit_instruction.strip():
                    st.warning("Please enter an edit instruction.")
                else:
                    with st.spinner("AI is editing this section..."):
                        result = api_post("/section/edit", {
                            "gen_id": st.session_state.gen_id or 0,
                            "sec_id": st.session_state.section_questions[selected_edit_section]["sec_id"],
                            "section_name": selected_edit_section,
                            "current_content": current_content,
                            "edit_instruction": edit_instruction
                        }, timeout=120)

                    if result:
                        st.session_state.section_contents[selected_edit_section] = result["updated_content"]
                        # Rebuild full document
                        ctx = st.session_state.company_ctx
                        header = f"""# {st.session_state.selected_doc_type}

**Organization:** {ctx.get('company_name', 'Company')}
**Department:** {st.session_state.selected_dept}
**Generated by:** DocForge AI

---

"""
                        body_parts = []
                        for sec_name in sections:
                            c = st.session_state.section_contents.get(sec_name, "")
                            if c:
                                body_parts.append(f"## {sec_name}\n\n{c}")
                        st.session_state.full_document = header + "\n\n---\n\n".join(body_parts)
                        st.success("✅ Section updated!")
                        st.rerun()

        with col2:
            if st.button("📝 Manual Edit", use_container_width=True):
                manual_text = st.text_area(
                    "Edit content directly:",
                    value=current_content,
                    height=300,
                    key="manual_edit_text"
                )
                if st.button("Save Manual Edit"):
                    st.session_state.section_contents[selected_edit_section] = manual_text
                    st.success("Saved!")
                    st.rerun()

    st.markdown("---")
    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("← Back to Document"):
            st.session_state.step = 6
            st.rerun()
    with col_next:
        if st.button("Save & Export →", type="primary", use_container_width=True):
            st.session_state.step = 8
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 8: Save & Export (Publish / Download)
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.step == 8:
    st.markdown('<span class="step-badge">Step 8 of 8</span>', unsafe_allow_html=True)
    st.markdown("## 💾 Save & Export")
    st.markdown("---")

    ctx = st.session_state.company_ctx
    doc_type = st.session_state.selected_doc_type
    full_doc = st.session_state.full_document

    st.success(f"✅ **{doc_type}** is ready for export!")

    st.markdown(f"""
| Field | Value |
|---|---|
| Document | `{doc_type}` |
| Department | `{st.session_state.selected_dept}` |
| Company | `{ctx.get('company_name', '—')}` |
| Sections | `{len(st.session_state.sections)}` |
| gen_id | `{st.session_state.gen_id}` |
""")

    st.markdown("---")

    # ── Option 1: Publish to Notion ──────────────────────────────────────────
    st.markdown("### 📓 Publish to Notion")
    if st.button("🚀 Publish to Notion", use_container_width=True):
        with st.spinner("Publishing to Notion..."):
            result = api_post("/document/publish", {
                "gen_id": st.session_state.gen_id or 0,
                "doc_type": doc_type,
                "department": st.session_state.selected_dept,
                "gen_doc_full": full_doc,
                "company_context": ctx
            })
        if result:
            notion_url = result.get("notion_url", "")
            st.success(f"✅ Published to Notion!")
            st.markdown(f"[🔗 View in Notion]({notion_url})")

    st.markdown("---")

    # ── Option 2: Download as TXT (Markdown) ─────────────────────────────────
    st.markdown("### 📥 Download")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="⬇️ Download as Markdown (.md)",
            data=full_doc,
            file_name=f"{doc_type.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col2:
        st.download_button(
            label="⬇️ Download as Text (.txt)",
            data=full_doc,
            file_name=f"{doc_type.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("---")

    # ── Full Document Preview ─────────────────────────────────────────────────
    st.markdown("### 📄 Final Document Preview")
    with st.expander("View Full Document", expanded=False):
        st.markdown(full_doc)

    st.markdown("---")

    # ── Create Another Document ───────────────────────────────────────────────
    if st.button("➕ Create Another Document", type="primary", use_container_width=True):
        # Reset workflow but keep company context
        saved_ctx = st.session_state.company_ctx
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state["company_ctx"] = saved_ctx
        st.session_state["step"] = 2
        init_session()
        st.rerun()