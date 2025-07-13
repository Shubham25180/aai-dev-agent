from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from nexus_agent import NexusAgent
import json
import threading
import asyncio
from voice.voice_system import VoiceSystem
import tempfile
from agents.conversational_brain import ConversationalBrain
from fastapi import Request

app = FastAPI()

# Enable CORS for all origins (for dev; restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory state for toggles (replace with your real logic) ---
toggles = {
    "voice": True,
    "tts": True,
    "auto_scroll": True,
    "intent": False,
    "emotion": False,
}

# --- Global state (replace with orchestrator wiring) ---
listener_running = False
mood_intent_enabled = False
processing_status = "idle"  # or "processing"
transcript_queue = asyncio.Queue()

# --- Global VoiceSystem and Brain instance ---
voice_system = VoiceSystem()
brain = ConversationalBrain()

# --- Instantiate your agent ---
agent = NexusAgent()

# --- Chat Endpoint ---
# @app.post("/api/chat")
# async def chat(request: Request):
#     data = await request.json()
#     user_message = data.get("message")
#     result = agent.process_text(user_message)
#     return JSONResponse({"reply": result["llm_response"]})

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    text = data.get("text", "")
    print(f"[API] /chat called with text: {text}")
    if not text:
        print("[API] /chat: No input provided.")
        return {"response": "No input provided."}
    # Route to ConversationalBrain (LLM)
    if hasattr(brain, 'respond'):
        # If respond is async
        import inspect
        if inspect.iscoroutinefunction(brain.respond):
            result = await brain.respond(text, context=None)
        else:
            result = brain.respond(text, context=None)
        # Assume result is dict with 'response' or just a string
        if isinstance(result, dict) and 'response' in result:
            print(f"[API] /chat: LLM response: {result['response']}")
            return {"response": result['response']}
        elif isinstance(result, str):
            print(f"[API] /chat: LLM response: {result}")
            return {"response": result}
        else:
            print(f"[API] /chat: LLM response (other): {result}")
            return {"response": str(result)}
    print("[API] /chat: LLM not available.")
    return {"response": "LLM not available."}

# --- Toggle Endpoints ---
@app.get("/api/toggles")
def get_toggles():
    return toggles

@app.post("/api/toggles/{toggle_name}")
async def set_toggle(toggle_name: str, request: Request):
    data = await request.json()
    value = data.get("value")
    toggles[toggle_name] = value
    print(f"[API] /api/toggles/{toggle_name} set to {value}")
    return {"success": True, "toggle": toggle_name, "value": value}

# --- Status Endpoint ---
@app.get("/api/status")
def get_status():
    # TODO: Replace with your real status logic
    return {
        "memory": {"short_term": 1, "long_term": "N/A"},
        "voice": {"status": "Active"},
        "agent": {"status": "Processing"},
        "llm": {"status": "Connected"},
    }

# --- REST: Start/Stop Whisper Listener ---
@app.post("/voice/start")
def start_voice():
    started = voice_system.start()
    return {"status": "started" if started else "failed"}

@app.post("/voice/stop")
def stop_voice():
    stopped = voice_system.stop()
    return {"status": "stopped" if stopped else "failed"}

# --- REST: Toggle Mood/Intent Detection ---
@app.post("/features/mood_intent")
def set_mood_intent(enabled: bool):
    # Use ConversationalBrain's setters if available
    if hasattr(brain, 'set_intent_enabled'):
        brain.set_intent_enabled(enabled)
    if hasattr(brain, 'set_emotion_enabled'):
        brain.set_emotion_enabled(enabled)
    return {"mood_intent_enabled": enabled}

# --- REST: Upload GUI Recorder Audio ---
@app.post("/voice/upload")
def upload_audio(file: UploadFile = File(...)):
    if voice_system.recognizer is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        result = voice_system.recognizer.recognize_file(tmp_path)
        transcript = result.get("text", "")
        return {"transcript": transcript, "result": result}
    else:
        return {"error": "Recognizer not available"}

# --- WebSocket for Real-Time Chat (optional) ---
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                data = await websocket.receive_text()
                # Try to parse as JSON, fallback to raw string
                try:
                    msg_obj = json.loads(data)
                    user_message = msg_obj.get("message", data)
                except Exception:
                    user_message = data
                # Call agent logic
                result = agent.process_text(user_message)
                llm_response = result.get("llm_response") or result.get("reply") or "[No response]"
                await websocket.send_text(json.dumps({
                    "type": "chat_response",
                    "message": llm_response
                }))
            except Exception as e:
                # If it's a disconnect, break loop; else, send error
                from starlette.websockets import WebSocketDisconnect
                if isinstance(e, WebSocketDisconnect):
                    print(f"WebSocket disconnected: {e}")
                    break
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Error: {str(e)}"
                    }))
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        await websocket.close()

# --- WebSocket: Live Transcript Stream ---
import threading
import queue as thread_queue
transcript_queue = thread_queue.Queue()

def recognizer_transcript_callback(transcript):
    transcript_queue.put(transcript)

# Patch Recognizer to call our callback after each transcript
if voice_system.recognizer is not None:
    # Only patch if recognizer is not None and method exists
    if hasattr(voice_system.recognizer, "_recognize_loop"):
        orig_loop = voice_system.recognizer._recognize_loop
        def patched_loop(*args, **kwargs):
            self = voice_system.recognizer
            if self is None:
                return
            import numpy as np
            import sounddevice as sd
            import queue as q
            print("[DEBUG] Recognizer: Entered recognition loop (patched for transcript callback).")
            try:
                with sd.InputStream(
                    samplerate=self.sample_rate,
                    blocksize=8000,
                    dtype=np.float32,
                    channels=1,
                    callback=self._audio_callback
                ):
                    self.logger.info("Audio stream started")
                    buffer = np.array([], dtype=np.float32)
                    silence_threshold = 0.01
                    silence_duration_sec = 2.0
                    silence_samples = int(self.sample_rate * silence_duration_sec)
                    while self.running:
                        try:
                            audio_chunk = self.audio_queue.get(timeout=1.0)
                            buffer = np.concatenate([buffer, audio_chunk.flatten()])
                            if buffer.shape[0] >= silence_samples:
                                tail = buffer[-silence_samples:]
                                if np.max(np.abs(tail)) < silence_threshold:
                                    utterance = buffer[:-silence_samples]
                                    if utterance.shape[0] > 0:
                                        peak = np.max(np.abs(utterance))
                                        if peak > 0:
                                            utterance = utterance / peak
                                        if self.model is not None:
                                            segments, info = self.model.transcribe(
                                                utterance,
                                                beam_size=1,
                                                language=None,
                                                task="transcribe",
                                                vad_filter=False
                                            )
                                            transcript = " ".join([seg.text for seg in segments])
                                            recognizer_transcript_callback(transcript.strip())
                                            print(f"[TRANSCRIPT] {transcript.strip()}")
                                            self.logger.info(f"[TRANSCRIPT] {transcript.strip()}")
                                        else:
                                            self.logger.error("Whisper model is not loaded!")
                                    buffer = buffer[-silence_samples:]
                        except q.Empty:
                            continue
            except Exception as e:
                print("[DEBUG] Recognizer: Recognition loop error:", e)
                if self is not None and hasattr(self, 'error_logger'):
                    self.error_logger.error(f"Recognition loop error: {e}")
        voice_system.recognizer._recognize_loop = patched_loop

@app.websocket("/ws/transcripts")
async def transcripts_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            transcript = transcript_queue.get()
            if asyncio.iscoroutine(transcript):
                transcript = await transcript
            if not isinstance(transcript, str):
                transcript = str(transcript)
            await websocket.send_text(transcript)
    except WebSocketDisconnect:
        pass

# --- WebSocket: Model Processing Status ---
@app.websocket("/ws/status")
async def status_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            status = "processing" if voice_system.is_active else "idle"
            await websocket.send_text(status)
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass

@app.websocket("/ws/llm_stream")
async def llm_stream_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        try:
            msg = json.loads(data)
            prompt = msg.get("prompt", "")
        except Exception:
            prompt = data
        if not prompt:
            await websocket.send_text(json.dumps({"type": "error", "message": "No prompt provided."}))
            return
        # Stream tokens/chunks from LLM
        stream_fn = getattr(brain.llm_connector, 'stream_prompt', None)
        if stream_fn is not None:
            try:
                for chunk in stream_fn(prompt):
                    await websocket.send_text(json.dumps({"type": "llm_token", "token": chunk}))
                await websocket.send_text(json.dumps({"type": "llm_done"}))
            except Exception as e:
                await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        else:
            await websocket.send_text(json.dumps({"type": "error", "message": "LLM streaming not supported."}))
    except WebSocketDisconnect:
        print("[WS] Client disconnected from /ws/llm_stream")
    except Exception as e:
        print(f"[WS] Error in /ws/llm_stream: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 