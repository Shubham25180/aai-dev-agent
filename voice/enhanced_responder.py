#!/usr/bin/env python3
"""
Enhanced TTS responder that automatically uses premium voices when available
"""

import os
from voice.responder import Responder
from utils.logger import get_action_logger, get_error_logger

class EnhancedResponder:
    """
    Enhanced TTS that automatically uses premium voices when available,
    falls back to regular TTS when not.
    """
    
    def __init__(self, rate=180, volume=1.0, voice=None):
        self.logger = get_action_logger('enhanced_voice_responder')
        self.error_logger = get_error_logger('enhanced_voice_responder')
        
        # Check if premium TTS is available
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        
        if self.api_key:
            try:
                from voice.premium_responder import PremiumResponder
                self.premium_tts = PremiumResponder()
                self.regular_tts = None
                self.logger.info("Premium TTS initialized successfully")
            except Exception as e:
                self.logger.warning(f"Premium TTS failed to initialize: {e}")
                self.premium_tts = None
                self.regular_tts = Responder(rate, volume, voice)
        else:
            self.premium_tts = None
            self.regular_tts = Responder(rate, volume, voice)
            self.logger.info("Using regular TTS (no premium API key found)")

    def speak(self, text, use_premium=True):
        """Speak text using the best available TTS."""
        try:
            if use_premium and self.premium_tts:
                self.logger.info("Using premium TTS")
                return self.premium_tts.speak(text)
            elif self.regular_tts:
                self.logger.info("Using regular TTS")
                return self.regular_tts.speak(text)
            else:
                self.logger.error("No TTS available")
                return False
                
        except Exception as e:
            self.error_logger.error(f"TTS error: {e}")
            # Fallback to regular TTS
            if self.regular_tts:
                return self.regular_tts.speak(text)
            return False

    def get_status(self):
        """Get TTS status information."""
        if self.premium_tts:
            status = self.premium_tts.get_status()
            status['type'] = 'premium'
            return status
        elif self.regular_tts:
            status = self.regular_tts.get_status()
            status['type'] = 'regular'
            return status
        else:
            return {'status': 'not_available', 'type': 'none'}

    def get_available_voices(self):
        """Get list of available voices."""
        if self.premium_tts:
            return self.premium_tts.get_available_voices()
        elif self.regular_tts:
            return self.regular_tts.get_available_voices()
        else:
            return []

    def set_voice(self, voice):
        """Set voice for TTS."""
        if self.premium_tts:
            self.premium_tts.set_voice(voice)
        elif self.regular_tts:
            self.regular_tts.set_voice(voice)

    def set_rate(self, rate):
        """Set speech rate."""
        if self.regular_tts:
            self.regular_tts.set_rate(rate)

    def set_volume(self, volume):
        """Set speech volume."""
        if self.regular_tts:
            self.regular_tts.set_volume(volume) 