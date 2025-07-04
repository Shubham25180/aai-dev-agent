from voice.responder import TTSResponder, Responder

if __name__ == "__main__":
    text = "Hello, I'm Nova, your assistant."
    try:
        print("[INFO] Trying edge-tts...")
        tts = TTSResponder(voice="en-US-AvaNeural")
        tts.speak(text)
        print("[SUCCESS] edge-tts spoke successfully.")
    except Exception as e:
        print(f"[WARN] edge-tts failed: {e}\nTrying fallback (pyttsx3/Windows TTS)...")
        try:
            responder = Responder()
            responder.speak(text)
            print("[SUCCESS] Fallback TTS spoke successfully.")
        except Exception as e2:
            print(f"[ERROR] All TTS methods failed: {e2}") 