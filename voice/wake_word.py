import vosk
import numpy as np
import queue
import json
import os

MODEL_PATH = os.environ.get("VOSK_MODEL_PATH", "model/vosk")
WAKE_WORD = "nexus"

class WakeWordDetector:
    def __init__(self, model_path=MODEL_PATH, wake_word=WAKE_WORD):
        self.model = vosk.Model(model_path)
        self.rec = vosk.KaldiRecognizer(self.model, 16000)
        self.wake_word = wake_word.lower()

    def process_chunk(self, chunk):
        if self.rec.AcceptWaveform(chunk.tobytes()):
            result = json.loads(self.rec.Result())
            text = result.get("text", "").lower()
            if self.wake_word in text:
                print(f"[WakeWordDetector] Wake word '{self.wake_word}' detected!")
                return True
        return False

# Example usage:
# detector = WakeWordDetector()
# for chunk in mic_listener.get_audio_chunk():
#     if detector.process_chunk(chunk):
#         # Trigger STT/emotion pipeline
#         pass 