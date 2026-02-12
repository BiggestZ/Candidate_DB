import streamlit as st
import requests

# API Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Candidate Search", page_icon="🔍")

st.title("🤖 Candidate Search Bot")
st.caption("AI-powered candidate search with natural language")

# Init. chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat Input
user_input = st.chat_input("Ask me to find candidates or chat with me...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # Call the /chat API
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"message": user_input},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()

        # Handle different intent types
        if result["intent"] == "search":
            # Format search results
            bot_message = result["message"]

            if result["data"] and result["data"]["candidates"]:
                candidates = result["data"]["candidates"]
                bot_message += "\n\n"

                for candidate in candidates:
                    bot_message += f"""
**{candidate['full_name']}**
- Email: {candidate['email']}
- Role: {candidate.get('role', 'N/A')}
- Score: {round(candidate['score'], 3)}
"""
                    if candidate.get('github_url'):
                        bot_message += f"- [GitHub]({candidate['github_url']})\n"
                    if candidate.get('linkedin_url'):
                        bot_message += f"- [LinkedIn]({candidate['linkedin_url']})\n"

                    bot_message += "\n---\n"

        elif result["intent"] == "chat":
            # Simple chat response
            bot_message = result["message"]

        else:
            # Unknown intent
            bot_message = result.get("message", "I'm not sure how to help with that.")

        st.session_state.messages.append(
            {"role": "assistant", "content": bot_message}
        )

    except requests.exceptions.ConnectionError:
        error_msg = "⚠️ Cannot connect to API. Make sure the API server is running on port 8000."
        st.session_state.messages.append(
            {"role": "assistant", "content": error_msg}
        )
    except Exception as e:
        error_msg = f"⚠️ Error: {str(e)}"
        st.session_state.messages.append(
            {"role": "assistant", "content": error_msg}
        )

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.write("This chatbot uses AI to understand your intent and search for candidates.")

    st.header("🔍 Example queries")
    st.code("Find senior Python developers")
    st.code("Show me React engineers")
    st.code("Search for ML engineers with 5+ years")

    st.divider()

    # API Status indicator
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Offline")
