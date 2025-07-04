import yaml
import os
import threading
import time
from typing import Dict, Any, Optional, Callable
from utils.logger import get_action_logger, get_error_logger
from .recognizer import Recognizer
from .responder import Responder, TTSResponder
from .commands import CommandProcessor

class VoiceSystem:
    """
    Main voice system coordinator using Whisper for multi-language speech recognition.
    Handles recognition, command processing, and text-to-speech responses.
    """
    
    def __init__(self, config_path='config/settings.yaml'):
        self.logger = get_action_logger('voice_system', subsystem='voice')
        self.error_logger = get_error_logger('voice_system', subsystem='voice')
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.recognizer = None
        self.responder = None
        self.command_processor = None
        self.is_active = False
        
        self._initialize_components()

    def _load_config(self):
        """Load voice system configuration."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            self.logger.info("Voice system configuration loaded")
            return config
        except Exception as e:
            self.error_logger.error(f"Failed to load voice config: {e}")
            return {}

    def _initialize_components(self):
        """Initialize voice recognition and response components."""
        try:
            voice_config = self.config.get('voice', {})
            
            # Initialize Whisper recognizer with multi-language support
            self.recognizer = Recognizer(
                model_size=voice_config.get('model_size', 'medium'),
                device=voice_config.get('device', 'cpu'),
                compute_type=voice_config.get('compute_type', 'int8')
            )
            
            # Initialize text-to-speech responder: try edge-tts first
            try:
                print("[DEBUG] VoiceSystem: Trying TTSResponder (edge-tts)...")
                self.responder = TTSResponder(voice=voice_config.get('tts_voice', 'en-US-AvaNeural'))
                self.logger.info("VoiceSystem: edge-tts TTSResponder initialized successfully")
                print("[DEBUG] VoiceSystem: edge-tts TTSResponder initialized successfully.")
                # Startup test: speak a test message and log result
                try:
                    self.logger.info("[TTSResponder] Startup test: speaking test message...")
                    print("[DEBUG] VoiceSystem: TTSResponder startup test: speaking test message...")
                    self.responder.speak("Edge TTS startup test: If you hear this, edge-tts is working.")
                    self.logger.info("[TTSResponder] Startup test succeeded: edge-tts is working.")
                    print("[DEBUG] VoiceSystem: TTSResponder startup test succeeded.")
                except Exception as e:
                    self.logger.error(f"[TTSResponder] Startup test FAILED: {e}")
                    print(f"[DEBUG] VoiceSystem: TTSResponder startup test FAILED: {e}")
            except Exception as e:
                self.logger.error(f"VoiceSystem: edge-tts TTSResponder failed: {e}, falling back to Responder (pyttsx3)")
                print(f"[DEBUG] VoiceSystem: edge-tts TTSResponder failed: {e}, falling back to Responder (pyttsx3)")
                self.responder = Responder(
                    rate=voice_config.get('tts_rate', 180),
                    volume=voice_config.get('tts_volume', 1.0)
                )
                print(f"[DEBUG] VoiceSystem: Fallback TTS engine in use: {type(self.responder).__name__}")
                self.logger.info(f"VoiceSystem: Fallback TTS engine in use: {type(self.responder).__name__}")
            
            # Initialize command processor
            self.command_processor = CommandProcessor(
                commands=voice_config.get('commands', [])
            )
            
            self.logger.info("Voice system components initialized successfully")
            
        except Exception as e:
            self.error_logger.error(f"Failed to initialize voice components: {e}")
            raise

    def start(self):
        """Start the voice system."""
        try:
            if not self.config.get('voice', {}).get('enabled', False):
                self.logger.warning("Voice system is disabled in configuration")
                return False
            if self.is_active:
                self.logger.warning("Voice system is already active")
                return True
            # Start recognition
            if self.recognizer is not None and self.recognizer.start():
                self.is_active = True
                self.logger.info("Voice system started successfully")
                if self.responder is not None:
                    self.responder.speak("Voice system activated. Ready for commands.")
                else:
                    print("[DEBUG] VoiceSystem: self.responder is None in start()!")
                    self.logger.error("VoiceSystem: responder is None in start()!")
                return True
            else:
                self.logger.error("Failed to start voice recognition")
                return False
        except Exception as e:
            self.error_logger.error(f"Failed to start voice system: {e}")
            return False

    def stop(self):
        """Stop the voice system."""
        try:
            if not self.is_active:
                return True
            if self.recognizer is not None:
                self.recognizer.stop()
            else:
                print("[DEBUG] VoiceSystem: self.recognizer is None in stop()!")
                self.logger.error("VoiceSystem: recognizer is None in stop()!")
            self.is_active = False
            self.logger.info("Voice system stopped")
            return True
        except Exception as e:
            self.error_logger.error(f"Failed to stop voice system: {e}")
            return False

    def listen_once(self, duration=5.0):
        """
        Listen for a single voice command.
        Args:
            duration: Recording duration in seconds
        Returns:
            dict: Recognition result with text, confidence, and language
        """
        try:
            if not self.is_active:
                self.logger.warning("Voice system not active, starting temporarily")
                if self.recognizer is not None:
                    self.recognizer.start()
                else:
                    print("[DEBUG] VoiceSystem: self.recognizer is None in listen_once()!")
                    self.logger.error("VoiceSystem: recognizer is None in listen_once()!")
                    return {'success': False, 'error': 'Recognizer not available'}
            if self.recognizer is not None:
                result = self.recognizer.recognize_once(duration)
            else:
                print("[DEBUG] VoiceSystem: self.recognizer is None in listen_once()!")
                self.logger.error("VoiceSystem: recognizer is None in listen_once()!")
                return {'success': False, 'error': 'Recognizer not available'}
            if result.get('success') and result.get('text'):
                self._process_command(result)
            return result
        except Exception as e:
            self.error_logger.error(f"Error during single listening: {e}")
            return {'success': False, 'error': str(e)}

    def _process_command(self, recognition_result):
        """
        Process recognized speech as a command.
        Args:
            recognition_result: Result from speech recognition
        """
        try:
            text = recognition_result.get('text', '')
            confidence = recognition_result.get('confidence', 0.0)
            language = recognition_result.get('language', 'unknown')
            self.logger.info(
                f"Processing command: '{text}' (lang: {language}, conf: {confidence:.2f})",
                extra={
                    'confidence': confidence,
                    'language': language,
                    'command_text': text
                }
            )
            # Check confidence threshold
            min_confidence = self.config.get('voice', {}).get('min_confidence', 0.6)
            if confidence < min_confidence:
                if self.responder is not None:
                    self.responder.speak(f"Command not recognized clearly. Please repeat.")
                else:
                    print("[DEBUG] VoiceSystem: self.responder is None in _process_command()!")
                    self.logger.error("VoiceSystem: responder is None in _process_command()!")
                return
            # Process command
            if self.command_processor is not None:
                command_result = self.command_processor.process(text)
            else:
                print("[DEBUG] VoiceSystem: self.command_processor is None in _process_command()!")
                self.logger.error("VoiceSystem: command_processor is None in _process_command()!")
                command_result = {'success': False}
            if command_result.get('success'):
                if self.responder is not None:
                    self.responder.speak(f"Executing: {command_result.get('action')}")
                else:
                    print("[DEBUG] VoiceSystem: self.responder is None in _process_command()!")
                    self.logger.error("VoiceSystem: responder is None in _process_command()!")
                self.logger.info(f"Command executed: {command_result}")
            else:
                if self.responder is not None:
                    self.responder.speak("Command not understood. Please try again.")
                else:
                    print("[DEBUG] VoiceSystem: self.responder is None in _process_command()!")
                    self.logger.error("VoiceSystem: responder is None in _process_command()!")
        except Exception as e:
            self.error_logger.error(f"Error processing command: {e}")
            if self.responder is not None:
                self.responder.speak("Error processing command.")
            else:
                print("[DEBUG] VoiceSystem: self.responder is None in _process_command() exception!")
                self.logger.error("VoiceSystem: responder is None in _process_command() exception!")

    def get_status(self):
        """Get current voice system status."""
        return {
            'active': self.is_active,
            'enabled': self.config.get('voice', {}).get('enabled', False),
            'model_info': self.recognizer.get_model_info() if self.recognizer else None,
            'supported_languages': self.recognizer.get_supported_languages() if self.recognizer else []
        }

    def test_recognition(self, duration=3.0):
        """
        Test speech recognition functionality.
        Args:
            duration: Test recording duration
        Returns:
            dict: Test results
        """
        try:
            self.logger.info("Starting recognition test...")
            if self.responder is not None:
                self.responder.speak("Testing speech recognition. Please speak now.")
            else:
                print("[DEBUG] VoiceSystem: self.responder is None in test_recognition()!")
                self.logger.error("VoiceSystem: responder is None in test_recognition()!")
            result = self.listen_once(duration)
            if result.get('success'):
                if self.responder is not None:
                    self.responder.speak(f"Test successful. Recognized: {result.get('text')}")
                else:
                    print("[DEBUG] VoiceSystem: self.responder is None in test_recognition()!")
                    self.logger.error("VoiceSystem: responder is None in test_recognition()!")
            else:
                if self.responder is not None:
                    self.responder.speak("Test failed. Please check microphone and try again.")
                else:
                    print("[DEBUG] VoiceSystem: self.responder is None in test_recognition()!")
                    self.logger.error("VoiceSystem: responder is None in test_recognition()!")
            return result
        except Exception as e:
            self.error_logger.error(f"Recognition test failed: {e}")
            return {'success': False, 'error': str(e)}

    def __del__(self):
        """Cleanup on destruction."""
        if self.is_active:
            self.stop() 