import sys, os
# Add project root to path (5 levels up from app.py)
project_root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
# print(project_root)
sys.path.insert(0, project_root)
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..",))

import streamlit as st
from Chatbot.gen_ai.retriever.search import search_candidates
from database.connection import get_conn


st.set_page_config(page_title="Candidate Search")

st.title("Candidate Search Bot")

# Init. chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add Intent Checking Here

# Chat Input
user_input = st.chat_input("Search for candidates...")

if user_input:
    # Add user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # Run search
    conn = get_conn()
    results = search_candidates(user_input)

    # Format response 
    if not results:
        response = "No candidates found."
    else:
        response = ""
        for r in results:
            response += f"""
            **{r['full_name']}***
            - Location: {r['location']}
            - Seniority: {r['seniority']}
            - Skills: {r['skills']}
            - Score: {round(r['score'], 3)}
            
            --- 
            """ # Need to add a score value for when search is done.

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])