import streamlit as st
import httpx

API_URL = "http://localhost:8000/api"

def render_generator_form():
    st.header("📄 Generate Document")

    with st.form("doc_form"):
        title = st.text_input("Document Title", placeholder="e.g. Data Retention Policy")

        col1, col2 = st.columns(2)
        with col1:
            industry = st.text_input("Industry", value="SaaS", disabled=True)
        with col2:
            doc_type = st.selectbox("Document Type", [
                "NDA", "Privacy Policy", "Terms of Service", "Employment Contract",
                "SLA", "Business Proposal", "Technical Spec", "Project Charter",
                "Risk Assessment", "Compliance Report", "Invoice Template",
                "Partnership Agreement"
            ])

        description = st.text_area("Description (optional)", placeholder="Brief context...")
        tags = st.text_input("Tags (comma separated)", placeholder="e.g. compliance, security")
        created_by = st.text_input("Created By", value="admin")

        submitted = st.form_submit_button("🚀 Generate Document")

    if submitted:
        if not title:
            st.error("Please enter a document title!")
            return

        with st.spinner("Generating document..."):
            try:
                response = httpx.post(f"{API_URL}/generate", json={
                    "title": title,
                    "industry": "SaaS",
                    "doc_type": doc_type,
                    "description": description,
                    "tags": [t.strip() for t in tags.split(",") if t.strip()],
                    "created_by": created_by
                }, timeout=60)

                if response.status_code == 200:
                    doc = response.json()
                    st.success("✅ Document generated successfully!")
                    st.session_state["last_doc"] = doc
                    st.session_state["published"] = False

                    st.subheader(doc["title"])
                    st.markdown(f"**Industry:** {doc['industry']} | **Type:** {doc['doc_type']} | **Version:** {doc['version']}")
                    st.markdown("---")
                    st.markdown(doc["content"])

                else:
                    st.error(f"Generation failed: {response.text}")
                    return

            except Exception as e:
                st.error(f"Error: {e}")
                return

    # Show publish button if a doc was generated and not yet published
    if st.session_state.get("last_doc") and not st.session_state.get("published"):
        st.markdown("---")
        if st.button("📓 Publish to Notion"):
            with st.spinner("Publishing to Notion..."):
                try:
                    doc = st.session_state["last_doc"]
                    pub = httpx.post(f"{API_URL}/publish", json=doc, timeout=30)
                    if pub.status_code == 200:
                        notion_url = pub.json().get("notion_url", "")
                        st.session_state["published"] = True
                        st.success("📓 Published to Notion!")
                        if notion_url:
                            st.markdown(f"[📝 View in Notion]({notion_url})")
                    else:
                        st.error(f"Publish failed: {pub.text}")
                except Exception as e:
                    st.error(f"Publish error: {e}")

    elif st.session_state.get("published"):
        st.success("✅ Document published to Notion!")
        if st.button("🔄 Generate New Document"):
            st.session_state.pop("last_doc", None)
            st.session_state.pop("published", None)
            st.rerun()