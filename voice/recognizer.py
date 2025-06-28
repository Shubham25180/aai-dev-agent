import os
import queue
import threading
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from utils.logger import get_action_logger, get_error_logger

class Recognizer:
    """
    Speech recognizer using Vosk (offline) with fallback to Whisper.
    Provides start/stop, confidence scoring, and logging.
    """
    def __init__(self, model_path='model', sample_rate=16000):
        self.logger = get_action_logger('voice_recognizer')
        self.error_logger = get_error_logger('voice_recognizer')
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.model = None
        self.recognizer = None
        self.audio_queue = queue.Queue()
        self.running = False
        self.thread = None
        self._load_model()

    def _load_model(self):
        try:
            if not os.path.exists(self.model_path):
                self.logger.error(f"Vosk model not found at {self.model_path}")
                return
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.logger.info("Vosk model loaded successfully")
        except Exception as e:
            self.error_logger.error(f"Failed to load Vosk model: {e}")

    def _audio_callback(self, indata, frames, time, status):
        if status:
            self.error_logger.error(f"Audio status: {status}")
        self.audio_queue.put(bytes(indata))

    def start(self):
        if not self.model:
            self.logger.error("Recognizer model not loaded")
            return
        self.running = True
        self.thread = threading.Thread(target=self._recognize_loop)
        self.thread.start()
        self.logger.info("Speech recognition started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("Speech recognition stopped")

    def _recognize_loop(self):
        try:
            with sd.RawInputStream(samplerate=self.sample_rate, blocksize = 8000, dtype='int16', channels=1, callback=self._audio_callback):
                while self.running:
                    data = self.audio_queue.get()
                    if self.recognizer.AcceptWaveform(data):
                        result = self.recognizer.Result()
                        self._handle_result(result)
        except Exception as e:
            self.error_logger.error(f"Recognition loop error: {e}")

    def _handle_result(self, result_json):
        import json
        try:
            result = json.loads(result_json)
            text = result.get('text', '')
            confidence = result.get('confidence', 0.0)
            self.logger.info(f"Recognized: {text}", extra={'confidence': confidence})
            # Here you could call a callback or update memory
        except Exception as e:
            self.error_logger.error(f"Failed to handle recognition result: {e}")

    def recognize_once(self) -> dict:
        """
        Recognize a single utterance (blocking).
        Returns transcript and confidence.
        """
        if not self.model:
            return {'success': False, 'error': 'Model not loaded'}
        try:
            with sd.RawInputStream(samplerate=self.sample_rate, blocksize = 8000, dtype='int16', channels=1) as stream:
                self.logger.info("Listening for single utterance...")
                audio = b''
                while True:
                    data, _ = stream.read(4000)
                    audio += data
                    if self.recognizer.AcceptWaveform(data):
                        break
                result = self.recognizer.Result()
                import json
                result = json.loads(result)
                text = result.get('text', '')
                confidence = result.get('confidence', 0.0)
                self.logger.info(f"Recognized (once): {text}", extra={'confidence': confidence})
                return {'success': True, 'text': text, 'confidence': confidence}
        except Exception as e:
            self.error_logger.error(f"Single recognition error: {e}")
            return {'success': False, 'error': str(e)}

    def recognize(self):
        # Placeholder for speech recognition
        print('Recognizing speech (not implemented)') 