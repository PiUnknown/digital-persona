import streamlit as st
from scraper.linkedin_scraper import get_linkedin_knowledge_base
from scraper.twitter_scraper import get_twitter_knowledge_base
from rag.chunker import chunk_text
from rag.embedder import build_faiss_index
from rag.chain import ask
from utils.validators import validate_linkedin_url, validate_twitter_handle

# ── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="Digital Persona",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Digital Persona")
st.caption("Explore anyone's professional profile through AI-powered conversation.")

# ── Session State Init ─────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "index" not in st.session_state:
    st.session_state.index = None
if "chunks" not in st.session_state:
    st.session_state.chunks = None
if "profile_loaded" not in st.session_state:
    st.session_state.profile_loaded = False
if "profile_name" not in st.session_state:
    st.session_state.profile_name = ""

# ── Sidebar: Profile Input ─────────────────────────────────
with st.sidebar:
    st.header("🔗 Load a Profile")

    linkedin_url = st.text_input(
        "LinkedIn URL (Required)",
        placeholder="https://www.linkedin.com/in/username/"
    )

    twitter_handle = st.text_input(
        "X (Twitter) Handle (Optional)",
        placeholder="@BillGates"
    )

    load_button = st.button("🚀 Load Profile", use_container_width=True)

    if st.session_state.profile_loaded:
        st.success(f"✅ Loaded: {st.session_state.profile_name}")
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.index = None
            st.session_state.chunks = None
            st.session_state.profile_loaded = False
            st.session_state.profile_name = ""
            st.rerun()

    st.divider()
    st.markdown("**How to use:**")
    st.markdown("1. Paste a LinkedIn profile URL")
    st.markdown("2. Optionally add a Twitter handle")
    st.markdown("3. Click Load Profile")
    st.markdown("4. Start asking questions!")

# ── Load Profile Logic ─────────────────────────────────────
if load_button and linkedin_url:

    # Validate LinkedIn URL
    is_valid, error_msg = validate_linkedin_url(linkedin_url)
    if not is_valid:
        st.error(f"❌ {error_msg}")

    # Validate Twitter handle if provided
    elif twitter_handle.strip() and not validate_twitter_handle(twitter_handle)[0]:
        _, tw_error = validate_twitter_handle(twitter_handle)
        st.error(f"❌ Twitter: {tw_error}")

    else:
        with st.spinner("🔍 Scraping LinkedIn profile..."):
            try:
                # Step 1: Scrape LinkedIn
                text = get_linkedin_knowledge_base(linkedin_url)

                # Step 2: Merge Twitter if provided
                if twitter_handle.strip():
                    try:
                        with st.spinner("🐦 Fetching Twitter/X data..."):
                            twitter_text = get_twitter_knowledge_base(twitter_handle)
                            text = text + "\n\n" + twitter_text
                            st.toast("✅ Twitter data merged!")
                    except Exception as e:
                        st.warning(f"⚠️ Twitter data unavailable, continuing with LinkedIn only: {str(e)}")

                # Step 3: Build RAG pipeline
                with st.spinner("🧠 Building knowledge base..."):
                    chunks = chunk_text(text)
                    index, chunks = build_faiss_index(chunks)

                # Step 4: Save to session
                st.session_state.index = index
                st.session_state.chunks = chunks
                st.session_state.profile_loaded = True
                st.session_state.chat_history = []

                # Extract name
                st.session_state.profile_name = "Unknown"
                for line in text.split("\n"):
                    if line.startswith("Name:"):
                        name = line.replace("Name:", "").strip()
                        if name:
                            st.session_state.profile_name = name
                        break

                st.rerun()

            except ValueError as e:
                st.error(f"❌ {str(e)}")
            except ConnectionError:
                st.error("❌ Could not connect to scraping service. Check your API token.")
            except RuntimeError as e:
                st.error(f"❌ Scraping failed: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

elif load_button and not linkedin_url:
    st.error("❌ LinkedIn URL is required.")

# ── Chat Interface ─────────────────────────────────────────
if st.session_state.profile_loaded:
    st.subheader(f"💬 Chat with {st.session_state.profile_name}'s Profile")
    st.divider()

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask something about this person...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    history_for_llm = st.session_state.chat_history[:-1]
                    answer = ask(
                        user_input,
                        st.session_state.index,
                        st.session_state.chunks,
                        history_for_llm
                    )
                    st.markdown(answer)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:
                    st.error(f"❌ Error generating response: {str(e)}")

else:
    # Empty state
    st.info("👈 Enter a LinkedIn URL in the sidebar and click **Load Profile** to get started.")
    st.markdown("### 💡 Example questions you can ask:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- What are their current roles?")
        st.markdown("- What is their educational background?")
    with col2:
        st.markdown("- What topics do they care about?")
        st.markdown("- What has been their most recent career pivot?")