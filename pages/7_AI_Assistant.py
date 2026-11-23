"""Streamlit Page 7: AI Assistant.

Interactive RAG-powered conversational code assistant grounded in active review
results and the secure coding knowledge base.
"""
import streamlit as st
from utils.ui_helpers import render_header, render_sidebar_info, get_active_review
from agents.code_assistant_agent import CodeAssistantAgent

st.set_page_config(
    page_title="AI Assistant | AI Code Review",
    page_icon="💬",
    layout="wide"
)

render_sidebar_info()
render_header("AI Conversational Assistant", "RAG-powered assistant grounded in review findings and secure guidelines")

# Initialize assistant
if "assistant_agent" not in st.session_state:
    st.session_state["assistant_agent"] = CodeAssistantAgent()

assistant = st.session_state["assistant_agent"]
active = get_active_review()

# Session State for Chat History
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am your AI Code Review Assistant. I can explain detected vulnerabilities, "
                "guide you through remediation steps, and answer questions using our 20 secure coding guidelines."
            ),
            "citations": []
        }
    ]

# Status bar
c_status1, c_status2 = st.columns([2, 1])
with c_status1:
    if active:
        st.caption(f"Active Context: `{active.get('filename')}` ({str(active.get('detected_language')).capitalize()}) — {len(active.get('findings', []))} findings.")
    else:
        st.caption("No active review. General secure coding questions supported.")
with c_status2:
    if assistant.is_gemini_active:
        st.markdown("<span class='badge badge-teal'>Model: Gemini 2.5 Flash</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='badge badge-sage'>Mode: RAG Knowledge-Base Fallback</span>", unsafe_allow_html=True)

# Starter question suggestions
st.markdown("###### Quick Queries:")
sq_cols = st.columns(3)
sample_query = None
with sq_cols[0]:
    if st.button("How to fix SQL injection?", use_container_width=True):
        sample_query = "How do I fix the SQL injection vulnerability in the reviewed code?"
with sq_cols[1]:
    if st.button("Explain code smells found", use_container_width=True):
        sample_query = "Explain the code quality smells detected and why they matter."
with sq_cols[2]:
    if st.button("OWASP prevention guidance", use_container_width=True):
        sample_query = "What are the relevant OWASP secure coding guidelines for this project?"

# Render Chat History
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            st.caption("📚 References: " + ", ".join([f"`{c.get('source_file')}`" for c in msg["citations"]]))

# User input handling
user_input = st.chat_input("Ask a question about your code or security guidelines...") or sample_query

if user_input:
    # Append user message
    st.session_state["chat_messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process response
    with st.chat_message("assistant"):
        with st.spinner("Retrieving secure guidelines and synthesizing answer..."):
            resp = assistant.ask(
                question=user_input,
                review_context=active
            )
            answer_text = resp.get("answer", "No response generated.")
            citations = resp.get("citations", [])

            st.markdown(answer_text)
            if citations:
                st.caption("📚 References: " + ", ".join([f"`{c.get('source_file')}`" for c in citations]))

            st.session_state["chat_messages"].append({
                "role": "assistant",
                "content": answer_text,
                "citations": citations
            })
