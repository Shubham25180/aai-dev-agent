import streamlit as st
import json
from gui_hybrid.llm_planner import LLMPlanner
from agents.hybrid_llm_connector import HybridLLMConnector

# --- Model and prompt template setup ---
MODEL_PROMPTS = {
    'ollama': '''You are a GUI automation assistant.\nUser wants to: {user_intent}\nScreen context: {screen_context}\n\nPlan a GUI action. Return JSON with:\n- action: "click" or "type"\n- coords: [x, y] for clicks\n- text: text to type\n- confidence: 0-1''',
    'huggingface': '''You are a fast Q&A assistant.\nUser wants to: {user_intent}\nScreen context: {screen_context}\n\nReply with a simple action plan in JSON.''',
}

# --- Streamlit UI ---
st.set_page_config(page_title="Prompt Tuner", layout="wide")
st.title("🧠 Prompt Tuner & LLM Test UI")

# Model selection
model = st.selectbox("Select Model", list(MODEL_PROMPTS.keys()))

# Prompt template editing
prompt_template = st.text_area(
    "Prompt Template (edit as needed)",
    value=MODEL_PROMPTS[model],
    height=200,
    key=f"prompt_{model}"
)

# User intent and context input
user_intent = st.text_input("User Intent", "close discord after saving")
screen_context = st.text_area("Screen Context (JSON or text)", '{"ocr_text": "Save changes?", "buttons": [{"text": "Save", "coords": [200, 300]}, {"text": "Cancel", "coords": [400, 300]}]}', height=100)

# LLM/planner output
if st.button("Send to LLM & Planner"):
    # Format prompt
    try:
        context_obj = json.loads(screen_context)
    except Exception:
        context_obj = screen_context
    final_prompt = prompt_template.format(user_intent=user_intent, screen_context=context_obj)
    st.subheader("Final Prompt Sent to LLM:")
    st.code(final_prompt, language="text")

    # Run LLM and planner
    llm_connector = HybridLLMConnector({})
    planner = LLMPlanner(llm=llm_connector)
    with st.spinner("Querying LLM and planner..."):
        llm_response = llm_connector.generate(final_prompt)
        st.subheader("Raw LLM Response:")
        st.code(llm_response, language="json")
        plan = planner.plan_action(user_intent, context_obj)
        st.subheader("Parsed Action/Plan:")
        st.json(plan)

# (Optional) Save/load prompt templates (stub)
st.sidebar.header("Prompt Templates")
st.sidebar.info("Saving/loading prompt templates coming soon!") 