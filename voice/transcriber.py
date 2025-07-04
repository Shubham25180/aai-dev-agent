from faster_whisper import WhisperModel
import numpy as np

MODEL_SIZE = "small"
SAMPLE_RATE = 16000

class RealTimeTranscriber:
    def __init__(self, model_size=MODEL_SIZE):
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.buffer = []

    def add_chunk(self, chunk):
        print(f"[DEBUG] RealTimeTranscriber: Adding chunk of shape {chunk.shape}, dtype {chunk.dtype}")
        self.buffer.append(chunk)

    def transcribe_buffer(self):
        print(f"[DEBUG] RealTimeTranscriber: transcribe_buffer called. Buffer length: {len(self.buffer)}")
        if not self.buffer:
            print("[DEBUG] RealTimeTranscriber: Buffer is empty!")
            return ""
        audio = np.concatenate(self.buffer)
        print(f"[DEBUG] RealTimeTranscriber: Concatenated audio shape: {audio.shape}, dtype {audio.dtype}")
        segments, info = self.model.transcribe(audio, language="en", beam_size=1, word_timestamps=True)
        transcript = " ".join([seg.text for seg in segments])
        print(f"[DEBUG] RealTimeTranscriber: Transcript result: '{transcript}'")
        self.buffer = []  # Clear buffer after transcription
        return transcript

# Example usage:
# transcriber = RealTimeTranscriber()
# for chunk in mic_listener.get_audio_chunk():
#     transcriber.add_chunk(chunk)
#     # When triggered, call transcriber.transcribe_buffer() 