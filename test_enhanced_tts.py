#!/usr/bin/env python3
"""
Test enhanced TTS system
"""

import os

def test_enhanced_tts():
    print("🎤 Testing Enhanced TTS System...")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if api_key:
        print(f"✅ Premium API key found: {api_key[:10]}...")
    else:
        print("ℹ️  No premium API key found, will use regular TTS")
    
    try:
        # Try to import and test enhanced TTS
        from voice.enhanced_responder import EnhancedResponder
        
        # Initialize TTS
        tts = EnhancedResponder(rate=200, volume=0.8)
        
        # Get status
        status = tts.get_status()
        print(f"📊 TTS Status: {status}")
        
        # Test speaking
        test_text = "Hello! I am NOVA, your sarcastic AI assistant with enhanced voice capabilities!"
        print(f"\n🎵 Speaking: {test_text}")
        
        success = tts.speak(test_text)
        
        if success:
            print("✅ Enhanced TTS test completed successfully!")
            return True
        else:
            print("❌ Enhanced TTS test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_tts()
    
    if success:
        print("\n🎉 Enhanced TTS is ready for NOVA!")
        print("\n💡 To use with NOVA:")
        print("1. Make sure your API key is set: set ELEVENLABS_API_KEY=your_key")
        print("2. Update NOVA to use EnhancedResponder instead of regular Responder")
        print("3. Enjoy premium-quality voice responses!")
    else:
        print("\n❌ Enhanced TTS test failed. Check your setup.") 