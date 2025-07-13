#!/usr/bin/env python3
"""
Test script for the new speech buffering system.
Demonstrates how speech is continuously collected and concatenated.
"""

import time
import threading
from voice.always_on_audio import AlwaysOnAudioPipeline

def test_transcript_callback(transcript, whisper_time, total_time):
    """Callback to handle transcripts."""
    print(f"\n🎤 TRANSCRIPT: '{transcript}'")
    print(f"   ⏱️  Whisper: {whisper_time:.2f}s, Total: {total_time:.2f}s")
    print(f"   📝 Length: {len(transcript)} characters")
    print("-" * 50)

def main():
    print("🎯 Testing Speech Buffering System")
    print("=" * 50)
    print("This system will:")
    print("1. Continuously collect speech even during transcription")
    print("2. Concatenate overlapping speech into longer segments")
    print("3. Only transcribe when there's a clear pause")
    print("4. Never miss any speech")
    print("=" * 50)
    
    # Create audio pipeline with speech buffering
    pipeline = AlwaysOnAudioPipeline(
        whisper_model_size='base',  # Use smaller model for faster testing
        device='cpu',
        vad_mode=2,  # Moderate VAD aggressiveness
        vad_silence_ms=800,  # Wait 800ms of silence before processing
        on_transcript=test_transcript_callback
    )
    
    try:
        print("\n🎧 Starting audio pipeline...")
        pipeline.start()
        
        print("\n🗣️  SPEAK NOW! Try these scenarios:")
        print("1. Speak normally - should transcribe after pause")
        print("2. Speak, then speak again during transcription - should concatenate")
        print("3. Speak continuously - should wait for clear pause")
        print("4. Press Ctrl+C to stop")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping audio pipeline...")
        pipeline.stop()
        print("✅ Test completed!")

if __name__ == "__main__":
    main() 