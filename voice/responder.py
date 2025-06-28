import pyttsx3
from utils.logger import get_action_logger, get_error_logger

class Responder:
    """
    Text-to-speech responder using pyttsx3 (offline, cross-platform).
    Provides methods for speaking text, adjusting rate/voice, and logging.
    """
    def __init__(self, rate=180, volume=1.0, voice=None):
        self.logger = get_action_logger('voice_responder')
        self.error_logger = get_error_logger('voice_responder')
        self.engine = pyttsx3.init()
        self.set_rate(rate)
        self.set_volume(volume)
        if voice:
            self.set_voice(voice)
        self.logger.info("TTS engine initialized")

    def set_rate(self, rate):
        self.engine.setProperty('rate', rate)
        self.logger.info(f"TTS rate set to {rate}")

    def set_volume(self, volume):
        self.engine.setProperty('volume', volume)
        self.logger.info(f"TTS volume set to {volume}")

    def set_voice(self, voice):
        voices = self.engine.getProperty('voices')
        for v in voices:
            if voice.lower() in v.name.lower():
                self.engine.setProperty('voice', v.id)
                self.logger.info(f"TTS voice set to {v.name}")
                return
        self.logger.warning(f"Requested voice '{voice}' not found")

    def speak(self, text):
        try:
            self.logger.info(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.error_logger.error(f"TTS error: {e}") 