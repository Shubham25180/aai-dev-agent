import requests
import json
from utils.prompt_loader import PromptLoader
from utils.context_manager import ContextManager

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"  # Already quantized (q4_0) by default

prompt_loader = PromptLoader()
context_manager = ContextManager()

def nexus_ollama_stream(user_input: str):
    # Add utterance to context manager
    context_manager.add_utterance(user_input, speaker="User")
    session_summary = context_manager.get_session_summary()
    recent_context = context_manager.get_recent_context()
    # Assemble prompt
    prompt = prompt_loader.assemble_prompt(
        user_input=user_input,
        session_context=f"[SessionSummary]: {session_summary}\n[Recent]: {recent_context}"
    )
    # Stream response from Ollama
    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": True},
        stream=True
    )
    print("[nexus] ", end="", flush=True)
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode())
            print(data.get("response", ""), end="", flush=True)
    print()  # Newline after completion

# Example usage:
# nexus_ollama_stream("What's the weather today?") 