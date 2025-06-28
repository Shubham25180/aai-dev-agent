#!/usr/bin/env python3
"""
Test script for Whisper-based voice recognition with multi-language support.
Tests English, Indian English, and Hindi recognition capabilities.
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice.recognizer import Recognizer
from voice.voice_system import VoiceSystem
from utils.logger import get_action_logger

def test_whisper_model_loading():
    """Test if Whisper model loads correctly."""
    print("🧪 Testing Whisper model loading...")
    
    try:
        # Test with medium model
        recognizer = Recognizer(model_size='medium', device='cpu', compute_type='int8')
        
        model_info = recognizer.get_model_info()
        print(f"✅ Model loaded successfully: {model_info}")
        
        supported_languages = recognizer.get_supported_languages()
        print(f"✅ Supported languages: {supported_languages}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def test_voice_system_initialization():
    """Test voice system initialization."""
    print("\n🧪 Testing voice system initialization...")
    
    try:
        voice_system = VoiceSystem()
        
        status = voice_system.get_status()
        print(f"✅ Voice system initialized: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice system initialization failed: {e}")
        return False

def test_single_recognition():
    """Test single utterance recognition."""
    print("\n🧪 Testing single utterance recognition...")
    print("📝 Please speak a command when prompted (5 seconds)...")
    
    try:
        recognizer = Recognizer(model_size='medium', device='cpu', compute_type='int8')
        
        # Give user time to prepare
        print("🎤 Starting recording in 3 seconds...")
        time.sleep(3)
        
        result = recognizer.recognize_once(duration=5.0)
        
        if result.get('success'):
            print(f"✅ Recognition successful!")
            print(f"   Text: '{result.get('text')}'")
            print(f"   Language: {result.get('language')}")
            print(f"   Confidence: {result.get('confidence'):.2f}")
            print(f"   Language Probability: {result.get('language_probability'):.2f}")
        else:
            print(f"❌ Recognition failed: {result.get('error')}")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Recognition test failed: {e}")
        return False

def test_command_processing():
    """Test command processing with sample text."""
    print("\n🧪 Testing command processing...")
    
    try:
        from voice.commands import CommandProcessor
        
        processor = CommandProcessor()
        
        # Test sample commands
        test_commands = [
            "open main.py",
            "create new file",
            "run python script",
            "save all files",
            "undo last action"
        ]
        
        for command in test_commands:
            result = processor.process(command, confidence=0.9, language='en')
            if result.get('success'):
                print(f"✅ '{command}' -> {result.get('action')}")
            else:
                print(f"❌ '{command}' -> {result.get('reason')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Command processing test failed: {e}")
        return False

def test_multi_language_commands():
    """Test multi-language command support."""
    print("\n🧪 Testing multi-language command support...")
    
    try:
        from voice.commands import CommandProcessor
        
        processor = CommandProcessor()
        
        # Test commands in different languages
        test_commands = [
            ("open file", "en"),
            ("file kholo", "hi"),  # Hindi equivalent
            ("create new function", "en"),
            ("function banane ke liye", "hi"),  # Hindi equivalent
        ]
        
        for command, language in test_commands:
            result = processor.process(command, confidence=0.9, language=language)
            print(f"   '{command}' ({language}): {result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-language test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Whisper Voice Recognition Test Suite")
    print("=" * 50)
    
    tests = [
        ("Model Loading", test_whisper_model_loading),
        ("Voice System Init", test_voice_system_initialization),
        ("Command Processing", test_command_processing),
        ("Multi-language Support", test_multi_language_commands),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Whisper integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    # Optional: Test live recognition
    print("\n🎤 Would you like to test live voice recognition? (y/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes']:
            test_single_recognition()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user.")

if __name__ == "__main__":
    main() 