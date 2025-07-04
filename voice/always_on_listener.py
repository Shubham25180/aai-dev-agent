import webrtcvad
import numpy as np
from voice.listener import MicListener
from voice.transcriber import RealTimeTranscriber
import soundfile as sf
import time

class AlwaysOnListener:
    def __init__(self, conversational_brain=None, aggressiveness=2, sample_rate=16000, chunk_duration=1.0):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.frame_duration_ms = 30  # 30ms frames
        self.frame_size = int(sample_rate * self.frame_duration_ms / 1000)
        self.listener = MicListener()
        self.transcriber = RealTimeTranscriber()
        self.conversational_brain = conversational_brain

    def is_speech(self, chunk):
        # chunk: np.ndarray, shape (chunk_size,)
        # Split chunk into 30ms frames
        num_frames = len(chunk) // self.frame_size
        for i in range(num_frames):
            frame = chunk[i * self.frame_size : (i + 1) * self.frame_size]
            if len(frame) < self.frame_size:
                continue  # skip incomplete frame
            audio_bytes = frame.astype(np.int16).tobytes()
            try:
                if self.vad.is_speech(audio_bytes, self.sample_rate):
                    return True
            except Exception as e:
                print(f"[VAD] Error processing frame: {e}")
                continue
        return False

    def run(self):
        print("[nexus] Always-on VAD listener started. Listening for utterances...")
        self.listener.start()
        buffer = []
        in_utterance = False
        utterance_count = 0
        for chunk in self.listener.get_audio_chunk():
            # chunk is (chunk_size,) int16
            if self.is_speech(chunk):
                buffer.append(chunk)
                in_utterance = True
            else:
                if in_utterance and buffer:
                    # End of utterance
                    utterance = np.concatenate(buffer)
                    print(f"[DEBUG] Utterance shape: {utterance.shape}, dtype: {utterance.dtype}")
                    # Normalize utterance audio
                    max_val = np.max(np.abs(utterance))
                    if max_val > 0:
                        utterance = utterance / max_val
                        utterance = (utterance * 32767).astype(np.int16)
                        print(f"[DEBUG] Utterance normalized (max: {max_val})")
                    # Save utterance to WAV for debugging
                    wav_filename = f"debug_utterance_{utterance_count}.wav"
                    sf.write(wav_filename, utterance, self.sample_rate)
                    print(f"[DEBUG] Saved utterance to {wav_filename}")
                    utterance_count += 1
                    # 2. Normalization (float32 in [-1, 1])
                    max_val = np.max(np.abs(utterance))
                    if max_val > 0:
                        utterance = utterance / max_val  # Now in [-1, 1]
                    utterance = utterance.astype(np.float32)
                    print(f"[DEBUG] To transcriber: min={utterance.min()}, max={utterance.max()}, dtype={utterance.dtype}")
                    # Save utterance to WAV for debugging (convert to int16 for saving)
                    wav_filename = f"debug_utterance_{utterance_count}.wav"
                    sf.write(wav_filename, (utterance * 32767).astype(np.int16), self.sample_rate)
                    print(f"[DEBUG] Saved utterance to {wav_filename}")
                    self.transcriber.add_chunk(utterance)
                    # Time STT (utterance to transcript)
                    stt_start = time.time()
                    transcript = self.transcriber.transcribe_buffer()
                    stt_end = time.time()
                    stt_duration = stt_end - stt_start
                    print(f"[DEBUG] STT time: {stt_duration:.2f} seconds")
                    if transcript.strip():
                        print(f"[nexus] Utterance transcript: {transcript}")
                        if self.conversational_brain:
                            llm_start = time.time()
                            response = self.conversational_brain.process_input(transcript, input_type='voice')
                            llm_end = time.time()
                            llm_duration = llm_end - llm_start
                            print(f"[DEBUG] LLM time: {llm_duration:.2f} seconds")
                            print(f"[nexus] Brain Response: {response.get('text')}")
                            if self.conversational_brain.tts_enabled:
                                self.conversational_brain.speak_response(response.get('text'))
                        if "nexus" in transcript.lower():
                            print("[nexus] (COMMAND DETECTED!) You addressed me directly.")
                    buffer = []
                in_utterance = False 