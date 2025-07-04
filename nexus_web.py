import streamlit as st
import time
from nexus_agent import NexusAgent

# --- UI Setup ---
st.set_page_config(page_title="Nexus AI Agent", layout="wide")

# Placeholder logo (emoji or text)
st.markdown("""
<div style='text-align: center;'>
    <span style='font-size: 64px;'>🧬</span>
    <h1 style='margin-bottom:0;'>Nexus</h1>
    <p style='font-size: 1.2em; color: #888;'>Your Always-On AI Agent</p>
</div>
<hr>
""", unsafe_allow_html=True)

# --- Session State for Chat and Prompts ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # List of dicts: {'user':..., 'mode':..., 'prompt':..., 'llm_response':..., 'plan':...}
if 'agent' not in st.session_state:
    st.session_state.agent = NexusAgent()
if 'prompt_template_automation' not in st.session_state:
    st.session_state.prompt_template_automation = (
        "You are Nexus, an AI assistant for GUI automation.\n"
        "User says: {user_message}\n"
        "Screen context: {screen_context}\n"
        "IMPORTANT: Only output valid JSON. Do not include any explanation, greeting, or extra text.\n"
        "Example output:\n{{\n  \"action\": \"click\", \"coords\": [100, 200], \"confidence\": 0.9\n}}"
    )
if 'prompt_template_chat' not in st.session_state:
    st.session_state.prompt_template_chat = (
        "You are Nexus, a helpful, witty, and context-aware AI assistant.\n"
        "User says: {user_message}\n"
        "Reply conversationally."
    )

# --- Prompt Template Editors ---
with st.expander("Prompt Template: Automation Mode (edit as needed)"):
    st.session_state.prompt_template_automation = st.text_area(
        "Automation Prompt Template:",
        value=st.session_state.prompt_template_automation,
        height=180,
        key="prompt_automation"
    )
with st.expander("Prompt Template: Chat Mode (edit as needed)"):
    st.session_state.prompt_template_chat = st.text_area(
        "Chat Prompt Template:",
        value=st.session_state.prompt_template_chat,
        height=120,
        key="prompt_chat"
    )

# --- Chat Interface ---
st.markdown("<h3>Conversation</h3>", unsafe_allow_html=True)
chat_box = st.container()

# Display chat history
for turn in st.session_state.chat_history:
    with chat_box:
        st.markdown(f"<div style='color:#0a0;font-weight:bold'>You:</div> <div style='margin-bottom:8px'>{turn['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<b>Mode:</b> {turn['mode'].capitalize()}", unsafe_allow_html=True)
        with st.expander("See prompt sent to LLM (brain)"):
            st.code(turn['prompt'], language="text")
        st.markdown(f"<div style='color:#0055aa;font-weight:bold'>Nexus (LLM reply):</div>", unsafe_allow_html=True)
        st.code(turn['llm_response'], language="json")
        st.markdown(f"<span style='color:#888'>⏱️ LLM response time: {turn.get('llm_response_time', 0):.2f} seconds</span>", unsafe_allow_html=True)
        if turn['plan'] is not None:
            st.markdown(f"<div style='color:#0055aa;font-weight:bold'>Nexus (Parsed plan):</div>", unsafe_allow_html=True)
            st.json(turn['plan'])

# --- User Input ---
user_input = st.text_input("Type your message to Nexus:", "", key="user_input")

# --- Send Button with Streaming ---
if st.button("Send") and user_input.strip():
    agent = st.session_state.agent
    # Pass the current prompt templates to the agent
    result = agent.process_text(
        user_input,
        prompt_template_automation=st.session_state.prompt_template_automation,
        prompt_template_chat=st.session_state.prompt_template_chat
    )
    # Streaming effect for LLM reply
    response_placeholder = st.empty()
    full = result['llm_response']
    streamed = ""
    for token in full.split():
        streamed += token + " "
        response_placeholder.code(streamed, language="json")
        time.sleep(0.04)
    # Add to chat history
    st.session_state.chat_history.append({
        'user': user_input,
        'mode': result['mode'],
        'prompt': result['prompt'],
        'llm_response': full,
        'plan': result['plan'],
        'llm_response_time': result['llm_response_time']
    })
    st.rerun() 