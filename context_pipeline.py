import json
import requests
import sys
import os
import numpy as np
import librosa

# --- CONFIG ---
AUDIO_FILE = sys.argv[1] if len(sys.argv) > 1 else "sample.wav"
SHORT_TERM_PATH = "memory/short_term.json"
PROMPT_PATH = "prompts/nexus_brain_init.prompt"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"  # Change as needed

# --- 1. Transcribe Audio ---
def transcribe_audio(audio_path):
    try:
        import whisper
    except ImportError:
        print("[WARN] Whisper not installed. Returning stub transcript.")
        return "This is a stub transcript."
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

# --- 2. Analyze Emotion (Real Audio Features) ---
def analyze_emotion(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=None)
        energy = float(np.mean(librosa.feature.rms(y=y)))
        pitch, _ = librosa.piptrack(y=y, sr=sr)
        avg_pitch = float(np.mean(pitch[pitch > 0])) if np.any(pitch > 0) else 0.0
        # Simple thresholds (tune as needed)
        if energy > 0.05 and avg_pitch > 180:
            emotion = "happy"
        elif energy < 0.02 and avg_pitch < 120:
            emotion = "sad"
        elif energy > 0.07:
            emotion = "angry"
        else:
            emotion = "neutral"
        return {
            "emotion": emotion,
            "energy": energy,
            "pitch": avg_pitch
        }
    except Exception as e:
        print(f"[WARN] Emotion analysis failed: {e}")
        return {"emotion": "neutral", "energy": 0.0, "pitch": 0.0}

# --- 3. Simulate Screen Context ---
def get_screen_context():
    # TODO: Replace with real OpenCV/MediaPipe analysis
    return {"app": "VSCode", "mouse": "idle", "face": "neutral"}

# --- 4. Update Short-Term Memory ---
def update_short_term(emotion, screen):
    if os.path.exists(SHORT_TERM_PATH):
        with open(SHORT_TERM_PATH, "r", encoding="utf-8") as f:
            short_term = json.load(f)
    else:
        short_term = {}
    short_term["emotional_context"] = emotion
    short_term["screen_context"] = screen
    with open(SHORT_TERM_PATH, "w", encoding="utf-8") as f:
        json.dump(short_term, f, indent=2)

# --- 5. Load LLM Brain Prompt ---
def load_brain_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

# --- 6. Build Full Prompt ---
def build_prompt(transcript, emotion, screen):
    # Stub memory/session context
    memory_summary = "(memory summary here)"
    session_context = "(session context here)"
    brain_prompt = load_brain_prompt()
    prompt = brain_prompt.replace("{{insert_memory_summary}}", memory_summary)
    prompt = prompt.replace("{{latest_session_snapshot}}", session_context)
    prompt += f"\nUser: {transcript}\nEmotion: {emotion}\nScreen: {screen}"
    return prompt

# --- 7. Query Ollama LLM ---
def query_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "[No response]")
    except Exception as e:
        return f"[LLM ERROR] {e}"

# --- MAIN PIPELINE ---
def main():
    print(f"[INFO] Using audio file: {AUDIO_FILE}")
    transcript = transcribe_audio(AUDIO_FILE)
    print(f"[INFO] Transcript: {transcript}")
    emotion = analyze_emotion(AUDIO_FILE)
    print(f"[INFO] Emotion: {emotion}")
    screen = get_screen_context()
    print(f"[INFO] Screen context: {screen}")
    update_short_term(emotion, screen)
    prompt = build_prompt(transcript, emotion, screen)
    print("[INFO] Sending prompt to LLM...")
    response = query_ollama(prompt)
    print("\n--- LLM Response ---\n")
    print(response)

if __name__ == "__main__":
    main() 