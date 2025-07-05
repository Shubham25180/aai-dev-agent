from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from nexus_agent import NexusAgent

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

# --- Instantiate your agent ---
agent = NexusAgent()

# --- Chat Endpoint ---
@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message")
    result = agent.process_text(user_message)
    return JSONResponse({"reply": result["llm_response"]})

# --- Toggle Endpoints ---
@app.get("/api/toggles")
def get_toggles():
    return toggles

@app.post("/api/toggles/{toggle_name}")
async def set_toggle(toggle_name: str, request: Request):
    data = await request.json()
    value = data.get("value")
    toggles[toggle_name] = value
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

# --- WebSocket for Real-Time Chat (optional) ---
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # TODO: Call your LLM/agent logic here
        await websocket.send_text(f"Echo: {data}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 