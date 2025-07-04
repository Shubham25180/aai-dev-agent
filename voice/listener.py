import sounddevice as sd
import numpy as np
import queue

# Audio stream config
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 1.0  # seconds
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

class MicListener:
    def __init__(self):
        self.q = queue.Queue()
        self.stream = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[MicListener] Status: {status}")
        self.q.put(indata.copy())

    def start(self):
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='int16',
            callback=self._callback,
            blocksize=CHUNK_SIZE
        )
        self.stream.start()
        print("[MicListener] Listening...")

    def get_audio_chunk(self):
        """Yields 1s audio chunks as numpy arrays."""
        while True:
            chunk = self.q.get()
            print(f"[DEBUG] MicListener: Got audio chunk of shape {chunk.shape}, dtype {chunk.dtype}")
            yield chunk.flatten()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            print("[MicListener] Stopped.")

# Example usage:
# listener = MicListener()
# listener.start()
# for chunk in listener.get_audio_chunk():
#     # Pass chunk to wake word/STT modules
#     pass 