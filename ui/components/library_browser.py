import streamlit as st
import httpx

API_URL = "http://localhost:8000/api"

def render_library_browser():
    st.header("📚 Document Library")

    try:
        response = httpx.get(f"{API_URL}/library", timeout=15)
        if response.status_code != 200:
            st.error(f"Failed to load library: {response.text}")
            return

        data = response.json()
        docs = data.get("documents", [])

        st.markdown(f"**Total Documents:** {data.get('total', 0)}")
        st.markdown("---")

        if not docs:
            st.info("No documents found in Notion database.")
            return

        # Build dynamic filter options from actual data
        industries = ["All"] + sorted(list(set(d["industry"] for d in docs if d.get("industry"))))
        doc_types = ["All"] + sorted(list(set(d["doc_type"] for d in docs if d.get("doc_type"))))

        col1, col2 = st.columns(2)
        with col1:
            filter_industry = st.selectbox("Filter by Industry", industries)
        with col2:
            filter_type = st.selectbox("Filter by Type", doc_types)

        filtered = docs
        if filter_industry != "All":
            filtered = [d for d in filtered if d.get("industry") == filter_industry]
        if filter_type != "All":
            filtered = [d for d in filtered if d.get("doc_type") == filter_type]

        st.markdown(f"**Showing:** {len(filtered)} documents")

        for doc in filtered:
            with st.expander(f"📄 {doc['title']} | {doc.get('industry', 'N/A')} | {doc.get('doc_type', 'N/A')}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Version", f"v{doc.get('version', '1')}")
                col2.metric("Status", doc.get("status", "Generated"))
                col3.metric("Word Count", doc.get("word_count", 0))

                tags = doc.get("tags", [])
                if tags:
                    st.markdown("**Tags:** " + " ".join([f"`{t}`" for t in tags]))

                st.markdown(f"**Created by:** {doc.get('created_by', 'AI Doc Generator')}")
                st.markdown(f"**Created at:** {doc.get('created_at', '')[:10]}")

                if doc.get("notion_url"):
                    st.markdown(f"[📝 View in Notion]({doc['notion_url']})")

    except httpx.ConnectError:
        st.error("❌ Cannot connect to backend. Make sure FastAPI is running: `uvicorn backend.main:app --reload`")
    except Exception as e:
        st.error(f"Error loading library: {e}")
