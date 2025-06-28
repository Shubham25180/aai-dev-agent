#!/usr/bin/env python3
"""
Test script for Hindi voice commands and multi-language integration.
Tests Hindi command patterns and their mapping to actions.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice.commands import CommandProcessor
from voice.voice_system import VoiceSystem

def test_hindi_commands():
    """Test Hindi command patterns."""
    print("🧪 Testing Hindi Command Patterns")
    print("=" * 50)
    
    processor = CommandProcessor()
    
    # Test Hindi commands
    hindi_commands = [
        # File operations
        ("file kholo", "hi", "open_file"),
        ("main.py kholo", "hi", "open_file"),
        ("file banane ke liye", "hi", "create_file"),
        ("function banane ke liye", "hi", "create_file"),
        ("class banane ke liye", "hi", "create_file"),
        ("file delete karo", "hi", "delete_file"),
        ("main.py hatao", "hi", "delete_file"),
        ("file edit karo", "hi", "edit_file"),
        ("code modify karo", "hi", "edit_file"),
        
        # Development operations
        ("code run karo", "hi", "run_command"),
        ("script chalane ke liye", "hi", "run_command"),
        ("variable banane ke liye", "hi", "edit_file"),
        
        # System operations
        ("undo karo", "hi", "undo"),
        ("pehle wala karo", "hi", "undo"),
        ("wapis karo", "hi", "undo"),
        ("save karo", "hi", "save"),
        ("file save karo", "hi", "save"),
        ("bachena", "hi", "save"),
        ("band karo", "hi", "exit"),
        ("exit karo", "hi", "exit"),
        ("quit karo", "hi", "exit"),
        
        # Navigation
        ("folder kholo", "hi", "navigate"),
        ("directory kholo", "hi", "navigate"),
        ("src folder mein jao", "hi", "navigate"),
        ("upar jao", "hi", "navigate_up"),
        ("parent folder mein jao", "hi", "navigate_up"),
        
        # Search
        ("function dhundho", "hi", "search"),
        ("error search karo", "hi", "search"),
        ("bug find karo", "hi", "search"),
        
        # Git operations
        ("git commit karo", "hi", "git_commit"),
        ("commit karo", "hi", "git_commit"),
        ("changes commit karo", "hi", "git_commit"),
        ("git push karo", "hi", "git_push"),
        ("push karo", "hi", "git_push"),
        ("remote mein push karo", "hi", "git_push"),
        ("git pull karo", "hi", "git_pull"),
        ("pull karo", "hi", "git_pull"),
        ("remote se pull karo", "hi", "git_pull"),
        
        # Testing
        ("test run karo", "hi", "run_tests"),
        ("testing karo", "hi", "run_tests"),
        ("unit test chalane ke liye", "hi", "run_tests"),
        ("debug karo", "hi", "debug"),
        ("debugging start karo", "hi", "debug"),
        
        # Documentation
        ("documentation banane ke liye", "hi", "create_docs"),
        ("docs banane ke liye", "hi", "create_docs"),
        ("readme update karo", "hi", "edit_readme"),
        ("readme edit karo", "hi", "edit_readme")
    ]
    
    passed = 0
    total = len(hindi_commands)
    
    for command, language, expected_action in hindi_commands:
        result = processor.process(command, confidence=0.9, language=language)
        
        if result.get('success') and result.get('command') == expected_action:
            print(f"✅ '{command}' -> {result.get('action')}")
            passed += 1
        else:
            print(f"❌ '{command}' -> Expected: {expected_action}, Got: {result.get('command', 'None')}")
    
    print(f"\n📊 Hindi Commands: {passed}/{total} passed")
    return passed == total

def test_english_commands():
    """Test English command patterns."""
    print("\n🧪 Testing English Command Patterns")
    print("=" * 50)
    
    processor = CommandProcessor()
    
    # Test English commands
    english_commands = [
        ("open main.py", "en", "open_file"),
        ("create new file", "en", "create_file"),
        ("delete test.py", "en", "delete_file"),
        ("edit config.py", "en", "edit_file"),
        ("run python script", "en", "run_command"),
        ("save", "en", "save"),
        ("undo", "en", "undo"),
        ("exit", "en", "exit"),
        ("quit", "en", "exit")
    ]
    
    passed = 0
    total = len(english_commands)
    
    for command, language, expected_action in english_commands:
        result = processor.process(command, confidence=0.9, language=language)
        
        if result.get('success') and result.get('command') == expected_action:
            print(f"✅ '{command}' -> {result.get('action')}")
            passed += 1
        else:
            print(f"❌ '{command}' -> Expected: {expected_action}, Got: {result.get('command', 'None')}")
    
    print(f"\n📊 English Commands: {passed}/{total} passed")
    return passed == total

def test_auto_language_detection():
    """Test automatic language detection."""
    print("\n🧪 Testing Auto Language Detection")
    print("=" * 50)
    
    processor = CommandProcessor()
    
    # Test mixed language commands
    mixed_commands = [
        ("open main.py", "auto"),
        ("file kholo", "auto"),
        ("create function", "auto"),
        ("function banane ke liye", "auto"),
        ("run tests", "auto"),
        ("test run karo", "auto")
    ]
    
    passed = 0
    total = len(mixed_commands)
    
    for command, language in mixed_commands:
        result = processor.process(command, confidence=0.9, language=language)
        
        if result.get('success'):
            print(f"✅ '{command}' -> {result.get('action')} (lang: {result.get('language')})")
            passed += 1
        else:
            print(f"❌ '{command}' -> {result.get('reason', 'Unknown error')}")
    
    print(f"\n📊 Auto Detection: {passed}/{total} passed")
    return passed == total

def test_voice_system_integration():
    """Test voice system integration."""
    print("\n🧪 Testing Voice System Integration")
    print("=" * 50)
    
    try:
        voice_system = VoiceSystem()
        status = voice_system.get_status()
        
        print(f"✅ Voice System Status: {status}")
        
        # Test command processing
        test_commands = [
            "open main.py",
            "file kholo",
            "create new function",
            "function banane ke liye"
        ]
        
        for command in test_commands:
            # Simulate voice recognition result
            recognition_result = {
                'success': True,
                'text': command,
                'confidence': 0.9,
                'language': 'en' if 'main.py' in command or 'create' in command else 'hi'
            }
            
            # Process through voice system
            voice_system._process_command(recognition_result)
            print(f"✅ Processed: '{command}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice system integration failed: {e}")
        return False

def test_command_statistics():
    """Test command statistics and availability."""
    print("\n🧪 Testing Command Statistics")
    print("=" * 50)
    
    processor = CommandProcessor()
    
    # Get statistics
    status = processor.get_status()
    print(f"📊 Total Commands: {status['total_commands']}")
    print(f"📊 Min Confidence: {status['min_confidence']}")
    print(f"📊 Supported Languages: {status['supported_languages']}")
    
    # Get available commands by language
    english_commands = processor.get_available_commands('en')
    hindi_commands = processor.get_available_commands('hi')
    
    print(f"📊 English Commands: {len(english_commands)}")
    print(f"📊 Hindi Commands: {len(hindi_commands)}")
    
    # Show some examples
    print("\n📝 English Command Examples:")
    for cmd in english_commands[:5]:
        print(f"   - {cmd['description']}")
    
    print("\n📝 Hindi Command Examples:")
    for cmd in hindi_commands[:5]:
        print(f"   - {cmd['description']}")
    
    return True

def main():
    """Run all tests."""
    print("🚀 Hindi Voice Commands Test Suite")
    print("=" * 60)
    
    tests = [
        ("Hindi Commands", test_hindi_commands),
        ("English Commands", test_english_commands),
        ("Auto Language Detection", test_auto_language_detection),
        ("Voice System Integration", test_voice_system_integration),
        ("Command Statistics", test_command_statistics)
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
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Hindi voice commands are working perfectly!")
        print("\n💡 You can now use Hindi commands like:")
        print("   - 'file kholo' (open file)")
        print("   - 'function banane ke liye' (create function)")
        print("   - 'test run karo' (run tests)")
        print("   - 'git commit karo' (commit changes)")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 