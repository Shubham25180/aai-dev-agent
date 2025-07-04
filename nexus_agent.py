from gui_hybrid.llm_planner import LLMPlanner
from agents.hybrid_llm_connector import HybridLLMConnector
import time
from memory.chroma_memory import ChromaMemory
# If you have a voice STT pipeline, import it here (stub for now)
# from voice.realtime_voice_system import RealTimeVoiceSystem

class NexusAgent:
    def __init__(self):
        self.llm_connector = HybridLLMConnector({})
        self.planner = LLMPlanner(llm=self.llm_connector)
        self.memory = ChromaMemory()
        # self.voice_system = RealTimeVoiceSystem()  # Stub for now
        # Add memory/context as needed

    def process_text(self, user_message: str, screen_context=None, prompt_template_automation=None, prompt_template_chat=None) -> dict:
        """
        Process text input. If the message is a chat/greeting/question, reply conversationally.
        If it's an automation request, return an action plan.
        Returns: dict with keys: mode, prompt, llm_response, plan, llm_response_time
        """
        if screen_context is None:
            screen_context = {"ocr_text": "Example screen", "buttons": []}
        # Retrieve relevant memories
        mem_context = self.memory.retrieve(user_message, n_results=3)
        mem_context_str = "".join([f"[Memory] {m}\n" for m in mem_context]) if mem_context else ""
        # Simple intent check: if user asks for click/type/open/run, treat as automation
        automation_keywords = ["click", "type", "open", "run", "save", "close", "move", "drag", "scroll"]
        if any(word in user_message.lower() for word in automation_keywords):
            # Automation mode
            if prompt_template_automation is None:
                prompt_template_automation = (
                    "You are Nexus, an AI assistant for GUI automation.\n"
                    "{mem_context}"
                    "User says: {user_message}\n"
                    "Screen context: {screen_context}\n"
                    "IMPORTANT: Only output valid JSON. Do not include any explanation, greeting, or extra text.\n"
                    "Example output:\n{{\n  \"action\": \"click\", \"coords\": [100, 200], \"confidence\": 0.9\n}}"
                )
            prompt = prompt_template_automation.format(mem_context=mem_context_str, user_message=user_message, screen_context=screen_context)
            start = time.time()
            llm_response = self.llm_connector.generate(prompt)
            elapsed = time.time() - start
            plan = self.planner.plan_action(user_message, screen_context)
            # Store user and agent turns in memory
            self.memory.store(f"User: {user_message}")
            self.memory.store(f"Nexus: {llm_response}")
            return {
                'mode': 'automation',
                'prompt': prompt,
                'llm_response': llm_response,
                'plan': plan,
                'llm_response_time': elapsed
            }
        else:
            # Conversational mode
            if prompt_template_chat is None:
                prompt_template_chat = (
                    "You are Nexus, a helpful, witty, and context-aware AI assistant.\n"
                    "{mem_context}"
                    "User says: {user_message}\n"
                    "Reply conversationally."
                )
            prompt = prompt_template_chat.format(mem_context=mem_context_str, user_message=user_message)
            start = time.time()
            llm_response = self.llm_connector.generate(prompt)
            elapsed = time.time() - start
            # Store user and agent turns in memory
            self.memory.store(f"User: {user_message}")
            self.memory.store(f"Nexus: {llm_response}")
            return {
                'mode': 'chat',
                'prompt': prompt,
                'llm_response': llm_response,
                'plan': None,
                'llm_response_time': elapsed
            }

    def process_voice(self, audio_bytes, screen_context=None) -> dict:
        """
        Process voice input (audio). Transcribe and handle as text.
        """
        # Stub: Replace with your real STT pipeline
        transcript = "[voice transcription not implemented]"
        # transcript = self.voice_system.transcribe(audio_bytes)
        return self.process_text(transcript, screen_context) 