import time
from typing import List, Dict

class ContextManager:
    def __init__(self, window_size: int = 5, summary_every: int = 10):
        self.window_size = window_size
        self.summary_every = summary_every
        self.conversation_history: List[Dict] = []
        self.session_summary = ""
        self.turn_count = 0

    def add_utterance(self, text: str, speaker: str = "User", timestamp: float = 0.0):
        self.turn_count += 1
        ts: float = float(timestamp) if timestamp else time.time()
        self.conversation_history.append({
            "text": text,
            "speaker": speaker,
            "timestamp": ts
        })
        if self.turn_count % self.summary_every == 0:
            self.summarize_session()

    def get_recent_context(self) -> str:
        recent = self.conversation_history[-self.window_size:]
        context = "\n".join([f"{u['speaker']}: {u['text']}" for u in recent])
        return context

    def summarize_session(self):
        # Simple summarizer: concatenate all texts and truncate (replace with LLM-based summary if available)
        all_text = " ".join([u['text'] for u in self.conversation_history])
        self.session_summary = all_text[:500] + ("..." if len(all_text) > 500 else "")

    def get_session_summary(self) -> str:
        return self.session_summary or self.get_recent_context()

    def get_latest_visual_context(self):
        """
        Retrieve the most recent visual context summary for prompt fusion.
        Returns: str or None
        """
        # TODO: Implement retrieval from memory/session
        return None

# Example usage:
# cm = ContextManager()
# cm.add_utterance("Hello nexus!", speaker="User")
# cm.add_utterance("Hi there!", speaker="nexus")
# print(cm.get_recent_context())
# print(cm.get_session_summary()) 