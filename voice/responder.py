import asyncio
import edge_tts
import tempfile
import os
import sys
import threading
import time
import platform
import pyttsx3
import subprocess
from utils.logger import get_action_logger, get_error_logger

class Responder:
    """
    Fallback/offline TTS engine for NEXUS. Uses pyttsx3 (offline, cross-platform) or Windows built-in TTS.
    Only used if edge-tts is unavailable or fails.
    """
    def __init__(self, rate=180, volume=1.0, voice=None):
        self.logger = get_action_logger('voice_responder', subsystem='voice')
        self.error_logger = get_error_logger('voice_responder', subsystem='voice')
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
        self.logger.debug(f"[Responder] About to speak: {text}")
        try:
            if self.engine:
                self.logger.info(f"[Responder] Speaking with pyttsx3: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
                return True
            else:
                self.logger.warning("[Responder] No TTS engine available, using fallback.")
                return self._speak_fallback(text)
        except Exception as e:
            self.error_logger.error(f"[Responder] TTS error: {e}")
            return self._speak_fallback(text)

    def _speak_fallback(self, text):
        """Fallback TTS using Windows built-in speech."""
        try:
            if platform.system().lower() == 'windows':
                # Clean and escape the text properly for PowerShell
                clean_text = text.replace('"', '""').replace("'", "''")
                # Remove any problematic characters
                clean_text = ''.join(char for char in clean_text if ord(char) < 128)
                
                # Use a simpler PowerShell command
                command = f'powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{clean_text}\')"'
                
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.logger.info("Fallback TTS worked")
                    return True
                else:
                    self.logger.warning(f"Fallback TTS failed: {result.stderr}")
                    # Try even simpler approach
                    return self._speak_simple_fallback(text)
            else:
                return False
                
        except Exception as e:
            self.error_logger.error(f"Fallback TTS error: {e}")
            return self._speak_simple_fallback(text)

    def _speak_simple_fallback(self, text):
        """Ultra-simple fallback TTS."""
        try:
            if platform.system().lower() == 'windows':
                # Use a very simple approach - just say "Response ready"
                command = 'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'Response ready\')"'
                
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.logger.info("Simple fallback TTS worked")
                    return True
                else:
                    self.logger.warning("All TTS methods failed")
                    return False
            else:
                return False
                
        except Exception as e:
            self.error_logger.error(f"Simple fallback TTS error: {e}")
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
                # Check if fallback methods work
                if platform.system().lower() == 'windows':
                    return {
                        'status': 'fallback_available',
                        'method': 'windows_powershell',
                        'note': 'Using Windows built-in TTS'
                    }
                else:
                    return {'status': 'not_available'}
                
            return {
                'status': 'available',
                'rate': self.engine.getProperty('rate'),
                'volume': self.engine.getProperty('volume'),
                'voice': self.engine.getProperty('voice')
            }
            
        except Exception as e:
            self.error_logger.error(f"Failed to get TTS status: {e}")
            return {'status': 'error', 'error': str(e)}

    def speak_with_emotion(self, text, emotion="neutral"):
        """
        Speak text with TTS, matching the given emotional tone if supported.
        Args:
            text (str): Text to speak
            emotion (str): Emotional tone (e.g., 'happy', 'sad', 'angry')
        """
        # TODO: Implement emotion-matched TTS (requires TTS engine with emotion control)
        self.speak(text)  # Fallback to normal TTS

    def backchannel_response(self):
        """
        Speak a natural backchannel phrase (e.g., 'mmhmm', 'Got it!').
        """
        # TODO: Implement with a list of natural backchannel phrases
        self.speak("Got it!")

class TTSResponder:
    """
    Default TTS engine for NEXUS. Uses edge-tts for modern, expressive, cloud-like voice output.
    Falls back to Responder (pyttsx3) for offline/local mode only.
    """
    def __init__(self, voice="en-US-AvaNeural"):
        self.voice = voice or "en-US-AvaNeural"
        self._loop = None
        self._thread = None
        import logging
        self.logger = logging.getLogger("voice.responder")
        self.logger.info(f"[TTSResponder] Initialized with voice: {self.voice}")
        self._start_event_loop()
        # Check for wmplayer on Windows
        if platform.system() == "Windows":
            from shutil import which
            if not which("wmplayer"):
                print("[WARNING] Windows Media Player (wmplayer) not found in PATH. edge-tts playback may fail.")
                self.logger.warning("Windows Media Player (wmplayer) not found in PATH. edge-tts playback may fail.")

    def _start_event_loop(self):
        if self._loop is None or not self._loop.is_running():
            self._loop = asyncio.new_event_loop()
            self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
            self._thread.start()
            time.sleep(0.1)  # Give the loop time to start

    async def _speak_async(self, text):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_path = f.name
        try:
            self.logger.info(f"[TTSResponder] edge-tts request: voice={self.voice}, text={text}")
            print(f"[DEBUG] TTSResponder: edge-tts request: voice={self.voice}, text={text}")
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(temp_path)
            # Play the mp3 (cross-platform)
            if platform.system() == "Windows":
                print(f"[DEBUG] TTSResponder: Playing with wmplayer: {temp_path}")
                os.system(f'start /min wmplayer "{temp_path}"')
            elif platform.system() == "Darwin":
                print(f"[DEBUG] TTSResponder: Playing with afplay: {temp_path}")
                os.system(f'afplay "{temp_path}"')
            else:
                print(f"[DEBUG] TTSResponder: Playing with mpg123: {temp_path}")
                os.system(f'mpg123 "{temp_path}"')
            # Wait for playback to finish (simple, not perfect)
            time.sleep(2)
        except Exception as e:
            self.logger.error(f"[TTSResponder] edge-tts error: {e} (voice={self.voice}, text={text})")
            print(f"[ERROR] TTSResponder: edge-tts error: {e} (voice={self.voice}, text={text})")
            raise  # Force error, do not silently fall back
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def speak(self, text):
        print(f"[DEBUG] TTSResponder.speak called with: {text}")
        self.logger.info(f"[TTSResponder] Speaking (edge-tts, {self.voice}): {text}")
        import logging
        logging.getLogger("voice.responder").debug(f"[TTSResponder] About to speak: {text}")
        if not self._loop or not self._loop.is_running():
            self._start_event_loop()
        if self._loop is None:
            raise RuntimeError("Event loop is not initialized.")
        try:
            fut = asyncio.run_coroutine_threadsafe(self._speak_async(text), self._loop)
            fut.result()
            print(f"[DEBUG] TTSResponder.speak finished successfully.")
        except Exception as e:
            self.logger.error(f"[TTSResponder] speak() error: {e} (voice={self.voice}, text={text})")
            print(f"[ERROR] TTSResponder.speak() error: {e} (voice={self.voice}, text={text})")
            raise  # Do not silently fall back

# Usage:
# tts = TTSResponder(voice="en-US-AvaNeural")
# tts.speak("Hello, this is Nexus!")

if __name__ == "__main__":
    print("--- edge-tts Voice Debug ---")
    import subprocess
    subprocess.run([sys.executable, "-m", "edge_tts", "--list-voices"])
    print("Default voice: en-US-AvaNeural") 