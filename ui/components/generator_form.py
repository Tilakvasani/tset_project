import streamlit as st
import httpx

API_URL = "http://localhost:8000/api"

DEPARTMENTS = [
    "Human Resources (HR)",
    "Legal",
    "Finance / Accounting",
    "Sales",
    "Marketing",
    "Engineering / Development",
    "Product Management",
    "Operations",
    "Customer Support",
    "Compliance / Risk Management",
]

DOC_TYPES = [
    "Terms of Service",
    "Employment Contract",
    "Privacy Policy",
    "SOP",
    "SLA",
    "Product Requirement Document",
    "Technical Specification",
    "Incident Report",
    "Security Policy",
    "Customer Onboarding Guide",
    "Business Proposal",
    "NDA",
]

SECTIONS = [
    {
        "name": "Title & Overview",
        "icon": "◈",
        "questions": [
            ("doc_title", "What is the official title of this document?", "e.g. Data Privacy Policy v2.0"),
            ("doc_version", "What version or effective date should appear?", "e.g. v1.0 — March 2026"),
        ]
    },
    {
        "name": "Purpose",
        "icon": "◎",
        "questions": [
            ("purpose_main", "What is the primary purpose of this document?", "e.g. Define data handling procedures for all employees"),
            ("purpose_problem", "What problem or business need does it address?", "e.g. GDPR compliance gap identified in Q1 audit"),
        ]
    },
    {
        "name": "Scope",
        "icon": "◐",
        "questions": [
            ("scope_applies", "Who does this document apply to?", "e.g. All full-time employees, contractors, and third-party vendors"),
            ("scope_exclusions", "Are there any exclusions or limitations?", "e.g. Does not apply to legacy systems pre-2020"),
        ]
    },
    {
        "name": "Responsibilities",
        "icon": "◑",
        "questions": [
            ("resp_implement", "Who is responsible for implementing this document?", "e.g. Department heads and team leads"),
            ("resp_maintain", "Who is responsible for maintaining and reviewing it?", "e.g. Legal team and CTO office"),
        ]
    },
    {
        "name": "Procedure / Process",
        "icon": "◒",
        "questions": [
            ("proc_steps", "Describe the main steps or process this document outlines.", "e.g. Data collection → encryption → storage → deletion after 90 days"),
            ("proc_tools", "Are there any tools, systems, or templates involved?", "e.g. Jira for tracking, Notion for documentation, AWS S3 for storage"),
        ]
    },
    {
        "name": "Compliance & Risk",
        "icon": "◓",
        "questions": [
            ("comp_regs", "What regulations or standards must this comply with?", "e.g. GDPR, SOC2, ISO 27001"),
            ("comp_risks", "What are the key risks if this document is not followed?", "e.g. Data breach, regulatory fines up to €20M"),
        ]
    },
    {
        "name": "Conclusion",
        "icon": "●",
        "questions": [
            ("conc_outcome", "What is the expected outcome after following this document?", "e.g. Full GDPR compliance and reduced breach risk by 80%"),
            ("conc_review", "How often should this document be reviewed or updated?", "e.g. Annually or after any major regulatory change"),
        ]
    },
]

def init_state():
    if "gen_step" not in st.session_state:
        st.session_state.gen_step = "config"
        st.session_state.gen_section = 0
        st.session_state.gen_answers = {}
        st.session_state.gen_config = {}
        st.session_state.last_doc = None
        st.session_state.published = False
        st.session_state.notion_url = ""

def progress_bar(current, total):
    pct = int((current / total) * 100)
    filled = int((current / total) * 20)
    bar = "█" * filled + "░" * (20 - filled)
    st.markdown(f"""
    <div style="margin: 1.5rem 0">
        <div style="display:flex; justify-content:space-between; margin-bottom:6px">
            <span style="font-family:'Space Mono',monospace; font-size:0.65rem; color:#7a7568; letter-spacing:0.1em; text-transform:uppercase">
                Section {current} of {total}
            </span>
            <span style="font-family:'Space Mono',monospace; font-size:0.65rem; color:#f5a623">{pct}%</span>
        </div>
        <div style="font-family:'Space Mono',monospace; font-size:0.75rem; color:#f5a623; letter-spacing:0.1em">{bar}</div>
    </div>
    """, unsafe_allow_html=True)

def section_breadcrumb():
    dots = []
    total = len(SECTIONS)
    current = st.session_state.gen_section
    for i, s in enumerate(SECTIONS):
        if i < current:
            color = "#f5a623"
            sym = "●"
        elif i == current:
            color = "#f5a623"
            sym = s["icon"]
        else:
            color = "#2e2b24"
            sym = "○"
        dots.append(f'<span style="color:{color}; font-size:0.8rem" title="{s["name"]}">{sym}</span>')
    st.markdown(f'<div style="display:flex; gap:8px; margin-bottom:1.5rem; align-items:center">{"".join(dots)}</div>', unsafe_allow_html=True)

def render_generator_form():
    init_state()

    # ── STEP 1: CONFIG ──────────────────────────────────────────────────
    if st.session_state.gen_step == "config":
        st.markdown('<div class="panel"><div class="panel-label">Document Setup</div>', unsafe_allow_html=True)

        with st.form("config_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Industry", value="SaaS", disabled=True)
            with col2:
                department = st.selectbox("Department", DEPARTMENTS)

            doc_type = st.selectbox("Document Type", DOC_TYPES)

            col3, col4 = st.columns(2)
            with col3:
                tags = st.text_input("Tags", placeholder="e.g. gdpr, b2b, enterprise")
            with col4:
                created_by = st.text_input("Author", value="admin")

            start = st.form_submit_button("◈  Begin Guided Generation →")

        st.markdown('</div>', unsafe_allow_html=True)

        if start:
            st.session_state.gen_config = {
                "industry": "SaaS",
                "department": department,
                "doc_type": doc_type,
                "tags": [t.strip() for t in tags.split(",") if t.strip()],
                "created_by": created_by,
            }
            st.session_state.gen_step = "questions"
            st.session_state.gen_section = 0
            st.rerun()

    # ── STEP 2: SECTION QUESTIONS ───────────────────────────────────────
    elif st.session_state.gen_step == "questions":
        cfg = st.session_state.gen_config
        sec_idx = st.session_state.gen_section
        section = SECTIONS[sec_idx]

        # Header
        st.markdown(f"""
        <div class="panel-label" style="margin-bottom:1rem">
            {section['icon']} {section['name'].upper()}
            &nbsp;·&nbsp;
            <span style="color:#7a7568">{cfg['doc_type']} · {cfg['department']} · SaaS</span>
        </div>
        """, unsafe_allow_html=True)

        progress_bar(sec_idx + 1, len(SECTIONS))
        section_breadcrumb()

        # Question card
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        with st.form(f"section_form_{sec_idx}"):
            for key, question, placeholder in section["questions"]:
                existing = st.session_state.gen_answers.get(key, "")
                st.text_area(
                    question,
                    value=existing,
                    placeholder=placeholder,
                    height=90,
                    key=f"input_{key}"
                )

            col1, col2 = st.columns([1, 3])
            with col1:
                back = st.form_submit_button("← Back") if sec_idx > 0 else None
            with col2:
                is_last = sec_idx == len(SECTIONS) - 1
                label = "◈  Generate Document" if is_last else "Next Section →"
                nxt = st.form_submit_button(label)

        st.markdown('</div>', unsafe_allow_html=True)

        if nxt:
            for key, question, _ in section["questions"]:
                val = st.session_state.get(f"input_{key}", "")
                st.session_state.gen_answers[key] = val

            if is_last:
                st.session_state.gen_step = "generating"
            else:
                st.session_state.gen_section += 1
            st.rerun()

        if back:
            st.session_state.gen_section -= 1
            st.rerun()

    # ── STEP 3: GENERATE ────────────────────────────────────────────────
    elif st.session_state.gen_step == "generating":
        cfg = st.session_state.gen_config
        ans = st.session_state.gen_answers

        description = f"""
Department: {cfg['department']}

TITLE & OVERVIEW:
- Document Title: {ans.get('doc_title', '')}
- Version/Date: {ans.get('doc_version', '')}

PURPOSE:
- Primary Purpose: {ans.get('purpose_main', '')}
- Business Need: {ans.get('purpose_problem', '')}

SCOPE:
- Applies To: {ans.get('scope_applies', '')}
- Exclusions: {ans.get('scope_exclusions', '')}

RESPONSIBILITIES:
- Implementation Owner: {ans.get('resp_implement', '')}
- Maintenance Owner: {ans.get('resp_maintain', '')}

PROCEDURE / PROCESS:
- Main Steps: {ans.get('proc_steps', '')}
- Tools & Systems: {ans.get('proc_tools', '')}

COMPLIANCE & RISK:
- Regulations: {ans.get('comp_regs', '')}
- Key Risks: {ans.get('comp_risks', '')}

CONCLUSION:
- Expected Outcome: {ans.get('conc_outcome', '')}
- Review Frequency: {ans.get('conc_review', '')}
        """.strip()

        title = ans.get('doc_title') or f"{cfg['doc_type']} — {cfg['department']}"

        with st.spinner("Generating your document..."):
            try:
                response = httpx.post(f"{API_URL}/generate", json={
                    "title": title,
                    "industry": "SaaS",
                    "doc_type": cfg["doc_type"],
                    "description": description,
                    "tags": cfg["tags"],
                    "created_by": cfg["created_by"],
                }, timeout=60)

                if response.status_code == 200:
                    doc = response.json()
                    st.session_state.last_doc = doc
                    st.session_state.published = False
                    st.session_state.gen_step = "result"
                    st.rerun()
                else:
                    st.error(f"Generation failed: {response.text}")
                    st.session_state.gen_step = "questions"
                    st.session_state.gen_section = len(SECTIONS) - 1
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.gen_step = "questions"

    # ── STEP 4: RESULT ──────────────────────────────────────────────────
    elif st.session_state.gen_step == "result":
        doc = st.session_state.last_doc
        cfg = st.session_state.gen_config

        st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1.5rem">
            <div>
                <div style="font-family:'Space Mono',monospace; font-size:0.65rem; color:#f5a623; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:4px">
                    ● Document Ready
                </div>
                <div style="font-family:'Playfair Display',serif; font-size:1.5rem; font-weight:700; color:#f0ede6">
                    {doc.get('title','')}
                </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end">
                <span class="chip chip-rose">{doc.get('doc_type','')}</span>
                <span class="chip chip-amber">{cfg.get('department','')}</span>
                <span class="chip chip-teal">v{doc.get('version','1.0')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="doc-card">
            <div class="doc-body">{doc.get('content','').replace(chr(10), '<br>')}</div>
            <div class="doc-footer">
                <div style="font-family:'Space Mono',monospace; font-size:0.65rem; color:#7a7568">
                    {len(doc.get('content','').split())} words · by {doc.get('created_by','admin')} · SaaS
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if not st.session_state.get("published"):
            col1, col2 = st.columns([2, 1])
            with col1:
                if st.button("◫  Publish to Notion"):
                    with st.spinner("Publishing..."):
                        try:
                            pub = httpx.post(f"{API_URL}/publish", json=doc, timeout=30)
                            if pub.status_code == 200:
                                st.session_state.notion_url = pub.json().get("notion_url", "")
                                st.session_state.published = True
                                st.success("Published to Notion!")
                                st.rerun()
                            else:
                                st.error(f"Publish failed: {pub.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
            with col2:
                if st.button("◈  New Document"):
                    for k in ["gen_step","gen_section","gen_answers","gen_config","last_doc","published","notion_url"]:
                        st.session_state.pop(k, None)
                    st.rerun()
        else:
            col1, col2 = st.columns([2, 1])
            with col1:
                notion_url = st.session_state.get("notion_url", "#")
                st.markdown(f'<a href="{notion_url}" target="_blank" class="notion-link">◫ View in Notion →</a>', unsafe_allow_html=True)
            with col2:
                if st.button("◈  New Document"):
                    for k in ["gen_step","gen_section","gen_answers","gen_config","last_doc","published","notion_url"]:
                        st.session_state.pop(k, None)
                    st.rerun()