import streamlit as st
import requests

API_URL = "http://localhost:8000"


def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_collection" not in st.session_state:
        st.session_state.current_collection = None
    if "collection_display_name" not in st.session_state:
        st.session_state.collection_display_name = None


def upload_pdf(uploaded_file):
    """Upload PDF to the API and return response."""
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    try:
        response = requests.post(f"{API_URL}/upload", files=files, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API server. Make sure FastAPI is running on port 8000.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Upload failed: {e.response.text}")
        return None


def query_document(collection_name: str, question: str, chat_history: list):
    """Send a question to the API."""
    payload = {
        "collection_name": collection_name,
        "question": question,
        "chat_history": chat_history,
    }
    try:
        response = requests.post(f"{API_URL}/query", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API server.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Query failed: {e.response.text}")
        return None


def get_collections():
    """Fetch list of collections from API."""
    try:
        response = requests.get(f"{API_URL}/collections", timeout=10)
        response.raise_for_status()
        return response.json().get("collections", [])
    except Exception:
        return []


def main():
    st.set_page_config(
        page_title="RAG PDF Chatbot",
        page_icon="📄",
        layout="wide",
    )

    init_session_state()

    # --- Sidebar ---
    with st.sidebar:
        st.header("📄 PDF Upload")

        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload a PDF to start asking questions about it.",
        )

        if uploaded_file is not None:
            if st.button("Process PDF", type="primary", use_container_width=True):
                with st.spinner("Processing PDF... This may take a moment."):
                    result = upload_pdf(uploaded_file)
                    if result:
                        st.session_state.current_collection = result["collection_name"]
                        st.session_state.collection_display_name = uploaded_file.name
                        st.session_state.chat_history = []
                        st.success(
                            f"Processed! {result['total_pages']} pages, "
                            f"{result['total_chunks']} chunks indexed."
                        )

        st.divider()

        # Show available collections
        st.subheader("Loaded Documents")
        collections = get_collections()
        if collections:
            for col_name in collections:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(
                        col_name[:25],
                        key=f"select_{col_name}",
                        use_container_width=True,
                    ):
                        st.session_state.current_collection = col_name
                        st.session_state.chat_history = []
                        st.rerun()
                with col2:
                    if st.button("🗑", key=f"del_{col_name}"):
                        try:
                            requests.delete(f"{API_URL}/collections/{col_name}", timeout=10)
                            if st.session_state.current_collection == col_name:
                                st.session_state.current_collection = None
                                st.session_state.chat_history = []
                            st.rerun()
                        except Exception:
                            st.error("Failed to delete.")
        else:
            st.caption("No documents loaded yet.")

    # --- Main Chat Area ---
    st.title("RAG PDF Chatbot")

    if st.session_state.current_collection:
        display_name = st.session_state.collection_display_name or st.session_state.current_collection
        st.caption(f"Chatting with: **{display_name}**")
    else:
        st.info("Upload a PDF in the sidebar to get started.")
        return

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"📑 Sources ({len(msg['sources'])} pages)"):
                    for src in msg["sources"]:
                        st.caption(f"**Page {src['page']}**: {src['text_snippet'][:250]}...")

    # Chat input
    if prompt := st.chat_input("Ask a question about your document..."):
        # Show user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = query_document(
                    st.session_state.current_collection,
                    prompt,
                    st.session_state.chat_history[:-1],  # Exclude current question
                )

            if result:
                st.markdown(result["answer"])
                sources = result.get("sources", [])

                if sources:
                    with st.expander(f"📑 Sources ({len(sources)} pages)"):
                        for src in sources:
                            st.caption(
                                f"**Page {src['page']}**: {src['text_snippet'][:250]}..."
                            )

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": sources,
                    }
                )
            else:
                error_msg = "Sorry, I couldn't process your question. Please try again."
                st.markdown(error_msg)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": error_msg}
                )


if __name__ == "__main__":
    main()
