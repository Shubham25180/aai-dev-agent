import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

# Test /api/status
try:
    r = requests.get(f"{BASE_URL}/api/status")
    print("/api/status:", r.status_code, r.json())
except Exception as e:
    print("/api/status failed:", e)

# Test /api/toggles
try:
    r = requests.get(f"{BASE_URL}/api/toggles")
    print("/api/toggles:", r.status_code, r.json())
except Exception as e:
    print("/api/toggles failed:", e)

# Test /api/chat
try:
    payload = {"message": "Hello, Nexus!"}
    r = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print("/api/chat:", r.status_code, r.json())
except Exception as e:
    print("/api/chat failed:", e)

# Test /ws/chat (WebSocket)
try:
    import asyncio
    import websockets
    async def test_ws():
        uri = f"ws://127.0.0.1:8000/ws/chat"
        async with websockets.connect(uri) as ws:
            await ws.send("Hello via WS!")
            reply = await ws.recv()
            print("/ws/chat: received:", reply)
    asyncio.run(test_ws())
except Exception as e:
    print("/ws/chat failed:", e) 