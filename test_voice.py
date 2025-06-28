#!/usr/bin/env python3
"""
Voice System Test Script
Tests the voice recognition, TTS, and command parsing functionality.
"""

import sys
import time
from app.bootstrap import Bootstrap
from utils.logger import get_action_logger, get_error_logger

def test_voice_system():
    """
    Test the voice system functionality.
    """
    logger = get_action_logger('voice_test')
    error_logger = get_error_logger('voice_test')
    
    print("🎤 Testing Voice System Integration")
    print("=" * 50)
    
    try:
        # Initialize bootstrap
        bootstrap = Bootstrap()
        result = bootstrap.bootstrap_application()
        
        if not result.get('success', False):
            print(f"❌ Bootstrap failed: {result.get('error', 'Unknown error')}")
            return False
        
        print("✅ Bootstrap completed successfully")
        
        # Get voice system components
        voice_system = bootstrap.get_component('voice_system')
        voice_handler = bootstrap.get_component('voice_handler')
        
        if not voice_system:
            print("❌ Voice system not available")
            return False
        
        print("✅ Voice system components loaded")
        
        # Test TTS functionality
        print("\n🔊 Testing Text-to-Speech...")
        voice_system.speak("Hello! This is a test of the voice system.")
        time.sleep(1)
        
        # Test voice system status
        status = voice_system.get_status()
        print(f"📊 Voice System Status: {status}")
        
        # Test command parsing
        print("\n🎯 Testing Command Parsing...")
        test_commands = [
            ("open test.txt", 0.9),
            ("run python main.py", 0.8),
            ("create new_file.py", 0.85),
            ("edit config.yaml", 0.9),
            ("undo", 0.95),
            ("save", 0.9),
            ("status", 0.95),
            ("help", 0.95)
        ]
        
        if voice_handler:
            for command_text, confidence in test_commands:
                print(f"Testing: '{command_text}' (confidence: {confidence})")
                result = voice_handler.handle_command(
                    command_text.split()[0], 
                    command_text.split()[1:] if len(command_text.split()) > 1 else [],
                    command_text
                )
                print(f"  Result: {result.get('success', False)}")
        else:
            print("❌ Voice handler not available")
        
        # Test single voice recognition (if model is available)
        if status.get('model_loaded', False):
            print("\n🎧 Testing Voice Recognition (Single Command)...")
            print("Please speak a command when prompted...")
            voice_system.speak("Please say a command now.")
            
            # Listen for a single command
            result = voice_system.listen_once()
            if result.get('success', False):
                print(f"✅ Recognized: '{result.get('text', '')}'")
                print(f"   Confidence: {result.get('confidence', 0.0)}")
            else:
                print(f"❌ Recognition failed: {result.get('error', 'Unknown error')}")
        else:
            print("\n⚠️  Voice recognition model not loaded")
            print("   To enable voice recognition, download a Vosk model and place it in the 'model/' directory")
        
        # Test interaction history
        history = voice_system.get_interaction_history()
        print(f"\n📝 Interaction History: {len(history)} entries")
        
        print("\n✅ Voice system test completed successfully!")
        return True
        
    except Exception as e:
        error_logger.error(f"Voice system test failed: {e}")
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        if 'bootstrap' in locals():
            bootstrap.shutdown()

def main():
    """
    Main test function.
    """
    print("AI Dev Agent - Voice System Test")
    print("=" * 40)
    
    success = test_voice_system()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 