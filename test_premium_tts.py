#!/usr/bin/env python3
"""
Test script for premium TTS using ElevenLabs API
"""

import os
import requests
import tempfile
import subprocess
import platform

def test_elevenlabs_tts():
    """Test ElevenLabs TTS API"""
    print("🎤 Testing Premium TTS (ElevenLabs)...")
    print("=" * 50)
    
    # Get API key from environment
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    if not api_key:
        print("❌ No ElevenLabs API key found!")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # ElevenLabs API configuration
    base_url = "https://api.elevenlabs.io/v1"
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    
    # Test text
    test_text = "Hello! I am NOVA, your sarcastic AI assistant with premium voice quality!"
    
    try:
        # Prepare the request
        url = f"{base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": test_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        print(f"🎵 Generating speech: {test_text}")
        
        # Make the API request
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            print("✅ Audio generated successfully!")
            print(f"📁 Saved to: {temp_file_path}")
            
            # Play the audio
            print("🔊 Playing audio...")
            success = play_audio(temp_file_path)
            
            # Clean up
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
            if success:
                print("✅ Premium TTS test completed successfully!")
                return True
            else:
                print("❌ Failed to play audio")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def play_audio(file_path):
    """Play audio file using system default player."""
    try:
        system = platform.system().lower()
        
        if system == "windows":
            subprocess.run(["start", file_path], shell=True, check=True)
            return True
        elif system == "darwin":  # macOS
            subprocess.run(["afplay", file_path], check=True)
            return True
        else:  # Linux
            subprocess.run(["aplay", file_path], check=True)
            return True
            
    except Exception as e:
        print(f"Error playing audio: {e}")
        return False

def get_usage_info():
    """Get ElevenLabs usage information."""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        return None
    
    try:
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }
        
        response = requests.get("https://api.elevenlabs.io/v1/user/subscription", headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "character_count": data.get("character_count", 0),
                "character_limit": data.get("character_limit", 0),
                "remaining": data.get("character_limit", 0) - data.get("character_count", 0)
            }
    except:
        pass
    
    return None

if __name__ == "__main__":
    # Check usage first
    usage = get_usage_info()
    if usage:
        print(f"📊 Usage: {usage['character_count']}/{usage['character_limit']} characters used")
        print(f"📊 Remaining: {usage['remaining']} characters")
        print()
    
    # Test TTS
    success = test_elevenlabs_tts()
    
    if success:
        print("\n🎉 Premium TTS is working! You can now integrate it with NOVA.")
        print("\n💡 To integrate with NOVA:")
        print("1. Update voice/responder.py to use ElevenLabs")
        print("2. Set your API key as environment variable")
        print("3. Enjoy premium-quality voice responses!")
    else:
        print("\n❌ Premium TTS test failed. Check your API key and try again.") 