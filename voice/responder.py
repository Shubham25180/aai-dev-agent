import pyttsx3
import platform
import subprocess
import os
from utils.logger import get_action_logger, get_error_logger

class Responder:
    """
    Text-to-speech responder using pyttsx3 (offline, cross-platform).
    Provides methods for speaking text, adjusting rate/voice, and logging.
    """
    def __init__(self, rate=180, volume=1.0, voice=None):
        self.logger = get_action_logger('voice_responder')
        self.error_logger = get_error_logger('voice_responder')
        self.engine = None
        
        # Try to initialize TTS engine
        self._init_tts_engine()
        
        if self.engine:
            self.set_rate(rate)
            self.set_volume(volume)
            
            # Set voice with fallback handling
            if voice:
                self.set_voice(voice)
            else:
                self._set_default_voice()
                
            self.logger.info("TTS engine configured successfully")
        else:
            self.logger.warning("TTS engine not available, will use fallback methods")

    def _init_tts_engine(self):
        """Initialize TTS engine with multiple fallback options."""
        try:
            # Try different initialization methods
            methods = [
                lambda: pyttsx3.init(),
                lambda: pyttsx3.init(driverName='sapi5'),
                lambda: pyttsx3.init(driverName='nsss'),
                lambda: pyttsx3.init(driverName='espeak')
            ]
            
            for method in methods:
                try:
                    self.engine = method()
                    self.logger.info("TTS engine initialized successfully")
                    return
                except Exception as e:
                    self.logger.warning(f"TTS method failed: {e}")
                    continue
            
            # If all methods fail, try Windows built-in TTS
            if platform.system().lower() == 'windows':
                self.logger.info("Trying Windows built-in TTS")
                # We'll use a fallback method for Windows
                
        except Exception as e:
            self.error_logger.error(f"Failed to initialize TTS engine: {e}")

    def _set_default_voice(self):
        """Set a default voice based on the operating system."""
        try:
            if not self.engine:
                self.logger.warning("TTS engine not available")
                return
                
            voices = self.engine.getProperty('voices')
            if not voices:
                self.logger.warning("No voices available")
                return
            
            # Platform-specific voice selection
            system = platform.system().lower()
            
            if system == 'windows':
                # Try to find any available voice
                for voice in voices:
                    try:
                        self.engine.setProperty('voice', voice.id)
                        self.logger.info(f"Set Windows voice: {voice.name}")
                        return
                    except:
                        continue
                
                # If no voice works, try the first one
                if voices:
                    self.engine.setProperty('voice', voices[0].id)
                    self.logger.info(f"Set fallback voice: {voices[0].name}")
                
            else:  # macOS/Linux
                # Use first available voice
                if voices:
                    self.engine.setProperty('voice', voices[0].id)
                    self.logger.info(f"Set default voice: {voices[0].name}")
                
        except Exception as e:
            self.error_logger.error(f"Failed to set default voice: {e}")

    def set_rate(self, rate):
        """Set speech rate."""
        try:
            if self.engine:
                self.engine.setProperty('rate', rate)
                self.logger.info(f"TTS rate set to {rate}")
        except Exception as e:
            self.error_logger.error(f"Failed to set TTS rate: {e}")

    def set_volume(self, volume):
        """Set speech volume."""
        try:
            if self.engine:
                self.engine.setProperty('volume', volume)
                self.logger.info(f"TTS volume set to {volume}")
        except Exception as e:
            self.error_logger.error(f"Failed to set TTS volume: {e}")

    def set_voice(self, voice):
        """Set specific voice by name."""
        try:
            if not self.engine:
                self.logger.warning("TTS engine not available")
                return
                
            voices = self.engine.getProperty('voices')
            for v in voices:
                if voice.lower() in v.name.lower():
                    self.engine.setProperty('voice', v.id)
                    self.logger.info(f"TTS voice set to {v.name}")
                    return
            
            self.logger.warning(f"Requested voice '{voice}' not found, using default")
            self._set_default_voice()
            
        except Exception as e:
            self.error_logger.error(f"Failed to set voice: {e}")
            self._set_default_voice()

    def speak(self, text):
        """Speak the given text."""
        try:
            if self.engine:
                self.logger.info(f"Speaking: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
                return True
            else:
                # Fallback: Use Windows built-in TTS
                return self._speak_fallback(text)
                
        except Exception as e:
            self.error_logger.error(f"TTS error: {e}")
            return self._speak_fallback(text)

    def _speak_fallback(self, text):
        """Fallback TTS using Windows built-in speech."""
        try:
            if platform.system().lower() == 'windows':
                # Use PowerShell to speak
                clean_text = text.replace('"', '\\"').replace("'", "\\'")
                command = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{clean_text}\')"'
                
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.logger.info("Fallback TTS worked")
                    return True
                else:
                    self.logger.warning(f"Fallback TTS failed: {result.stderr}")
                    return False
            else:
                return False
                
        except Exception as e:
            self.error_logger.error(f"Fallback TTS error: {e}")
            return False

    def get_available_voices(self):
        """Get list of available voices."""
        try:
            if not self.engine:
                return []
                
            voices = self.engine.getProperty('voices')
            return [{'id': v.id, 'name': v.name} for v in voices]
            
        except Exception as e:
            self.error_logger.error(f"Failed to get available voices: {e}")
            return []

    def get_status(self):
        """Get TTS engine status."""
        try:
            if not self.engine:
                return {'status': 'not_available'}
                
            return {
                'status': 'available',
                'rate': self.engine.getProperty('rate'),
                'volume': self.engine.getProperty('volume'),
                'voice': self.engine.getProperty('voice'),
                'available_voices': len(self.get_available_voices())
            }
            
        except Exception as e:
            self.error_logger.error(f"Failed to get TTS status: {e}")
            return {'status': 'error', 'error': str(e)} 