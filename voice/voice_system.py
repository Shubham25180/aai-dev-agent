import os
import threading
import time
from typing import Dict, Any, Optional, Callable
from utils.logger import get_action_logger, get_error_logger
from .recognizer import Recognizer
from .responder import Responder
from .commands import VoiceCommands

class VoiceSystem:
    """
    Integrated voice system that combines speech recognition, TTS, and command parsing.
    Provides a complete voice interface for the AI Dev Agent.
    """
    
    def __init__(self, config: Dict[str, Any], command_callback: Optional[Callable] = None):
        """
        Initialize the voice system with configuration and command callback.
        
        Args:
            config: Configuration dictionary with voice settings
            command_callback: Callback function to handle parsed commands
        """
        self.config = config
        self.logger = get_action_logger('voice_system')
        self.error_logger = get_error_logger('voice_system')
        
        # Voice settings from config
        voice_config = config.get('voice', {})
        self.model_path = voice_config.get('model_path', 'model')
        self.sample_rate = voice_config.get('sample_rate', 16000)
        self.min_confidence = voice_config.get('min_confidence', 0.6)
        self.tts_rate = voice_config.get('tts_rate', 180)
        self.tts_volume = voice_config.get('tts_volume', 1.0)
        
        # Initialize components
        self.recognizer = Recognizer(self.model_path, self.sample_rate)
        self.responder = Responder(self.tts_rate, self.tts_volume)
        self.command_parser = VoiceCommands(min_confidence=self.min_confidence)
        
        # System state
        self.is_active = False
        self.command_callback = command_callback
        self.recognition_thread = None
        
        # Voice interaction history
        self.interaction_history = []
        
        self.logger.info("Voice system initialized")

    def start(self) -> bool:
        """
        Start the voice system for continuous listening.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            if not self.recognizer.model:
                self.speak("Voice recognition model not available. Please check model installation.")
                return False
            
            self.is_active = True
            self.recognition_thread = threading.Thread(target=self._recognition_loop)
            self.recognition_thread.daemon = True
            self.recognition_thread.start()
            
            self.speak("Voice system activated. I'm listening for commands.")
            self.logger.info("Voice system started successfully")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to start voice system: {e}")
            return False

    def stop(self) -> bool:
        """
        Stop the voice system.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            self.is_active = False
            if self.recognition_thread:
                self.recognition_thread.join(timeout=2)
            
            self.speak("Voice system deactivated.")
            self.logger.info("Voice system stopped")
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to stop voice system: {e}")
            return False

    def _recognition_loop(self):
        """
        Main recognition loop that continuously listens for voice input.
        """
        try:
            while self.is_active:
                # Listen for a single utterance
                result = self.recognizer.recognize_once()
                
                if result.get('success', False):
                    text = result.get('text', '')
                    confidence = result.get('confidence', 0.0)
                    
                    if text.strip():  # Only process non-empty text
                        self._process_voice_input(text, confidence)
                else:
                    # Brief pause before next recognition attempt
                    time.sleep(0.1)
                    
        except Exception as e:
            self.error_logger.error(f"Recognition loop error: {e}")

    def _process_voice_input(self, text: str, confidence: float):
        """
        Process voice input through command parser and execute if valid.
        
        Args:
            text: Recognized text
            confidence: Recognition confidence score
        """
        try:
            # Log the voice input
            self.logger.info(f"Processing voice input: {text}", extra={'confidence': confidence})
            
            # Parse the command
            parsed = self.command_parser.interpret(text, confidence)
            
            # Store in interaction history
            self.interaction_history.append({
                'timestamp': time.time(),
                'text': text,
                'confidence': confidence,
                'parsed': parsed
            })
            
            if parsed.get('success', False):
                command = parsed.get('command')
                args = parsed.get('args', [])
                
                # Confirm the command
                self.speak(f"Executing command: {command}")
                
                # Execute via callback if available
                if self.command_callback:
                    try:
                        result = self.command_callback(command, args, text)
                        if result and result.get('success', False):
                            self.speak("Command executed successfully")
                        else:
                            self.speak("Command execution failed")
                    except Exception as e:
                        self.error_logger.error(f"Command execution error: {e}")
                        self.speak("An error occurred while executing the command")
                else:
                    self.logger.warning("No command callback available")
                    
            else:
                reason = parsed.get('reason', 'unknown')
                if reason == 'low_confidence':
                    self.speak("I didn't hear that clearly. Please repeat.")
                elif reason == 'no_match':
                    self.speak("I don't understand that command. Please try again.")
                else:
                    self.speak("I couldn't process that command.")
                    
        except Exception as e:
            self.error_logger.error(f"Voice input processing error: {e}")

    def speak(self, text: str):
        """
        Speak text using TTS.
        
        Args:
            text: Text to speak
        """
        try:
            self.responder.speak(text)
        except Exception as e:
            self.error_logger.error(f"TTS error: {e}")

    def listen_once(self) -> Dict[str, Any]:
        """
        Listen for a single voice command (blocking).
        
        Returns:
            Recognition result dictionary
        """
        try:
            self.logger.info("Listening for single command...")
            result = self.recognizer.recognize_once()
            
            if result.get('success', False):
                text = result.get('text', '')
                confidence = result.get('confidence', 0.0)
                
                if text.strip():
                    self._process_voice_input(text, confidence)
                    
            return result
            
        except Exception as e:
            self.error_logger.error(f"Single listen error: {e}")
            return {'success': False, 'error': str(e)}

    def add_custom_command(self, pattern: str, command: str):
        """
        Add a custom voice command pattern.
        
        Args:
            pattern: Regex pattern to match
            command: Command name to execute
        """
        try:
            self.command_parser.command_map[pattern] = command
            self.logger.info(f"Added custom command: {pattern} -> {command}")
        except Exception as e:
            self.error_logger.error(f"Failed to add custom command: {e}")

    def get_interaction_history(self, limit: int = 10) -> list:
        """
        Get recent voice interaction history.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interactions
        """
        return self.interaction_history[-limit:] if self.interaction_history else []

    def clear_history(self):
        """Clear voice interaction history."""
        self.interaction_history.clear()
        self.logger.info("Voice interaction history cleared")

    def get_status(self) -> Dict[str, Any]:
        """
        Get voice system status.
        
        Returns:
            Status dictionary
        """
        return {
            'is_active': self.is_active,
            'model_loaded': self.recognizer.model is not None,
            'interaction_count': len(self.interaction_history),
            'min_confidence': self.min_confidence,
            'tts_rate': self.tts_rate,
            'tts_volume': self.tts_volume
        } 