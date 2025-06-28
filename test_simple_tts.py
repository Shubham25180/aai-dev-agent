#!/usr/bin/env python3
"""
Simple TTS test
"""

from voice.responder import Responder

def main():
    print("🔊 Testing TTS...")
    
    # Initialize TTS
    tts = Responder(rate=200, volume=0.8)
    
    # Test speaking
    print("Speaking: Hello! I am NOVA, your sarcastic AI assistant.")
    success = tts.speak("Hello! I am NOVA, your sarcastic AI assistant.")
    
    if success:
        print("✅ TTS worked!")
    else:
        print("❌ TTS failed!")

if __name__ == "__main__":
    main() 