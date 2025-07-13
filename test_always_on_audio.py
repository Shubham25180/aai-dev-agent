import sys
import time
from voice.always_on_audio import AlwaysOnAudioPipeline

def on_transcript(transcript, whisper_time, total_time):
    print(f"\n[RESULT] Transcript: {transcript}")
    print(f"[RESULT] Whisper time: {whisper_time:.2f}s, Total: {total_time:.2f}s\n")

if __name__ == "__main__":
    # Optionally, allow device index as a command-line argument
    device = None
    if len(sys.argv) > 1:
        device = int(sys.argv[1])

    print("Starting AlwaysOnAudioPipeline in isolation...")
    pipeline = AlwaysOnAudioPipeline(
        whisper_model_size='medium',  # or 'base', etc.
        device='cpu',
        on_transcript=on_transcript
    )
    # If you want to set the device, you can add a device parameter to AlwaysOnAudioPipeline and pass it to InputStream
    pipeline.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping pipeline...")
        pipeline.stop()