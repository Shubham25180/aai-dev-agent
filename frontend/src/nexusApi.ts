// API client for connecting to Nexus FastAPI backend

export const API_BASE = "http://localhost:8000";

export interface ChatMessage {
  message: string;
}

export interface ChatResponse {
  response: string;
  status: string;
}

export interface StatusResponse {
  memory: {
    short_term: number;
    long_term: string;
  };
  voice: {
    status: string;
  };
  agent: {
    status: string;
  };
  llm: {
    status: string;
  };
}

export interface TogglesResponse {
  voice: boolean;
  tts: boolean;
  auto_scroll: boolean;
  intent: boolean;
  emotion: boolean;
}

export interface ToggleUpdate {
  voice?: boolean;
  tts?: boolean;
  auto_scroll?: boolean;
  intent?: boolean;
  emotion?: boolean;
}

// REST API calls
export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });
  
  if (!response.ok) {
    throw new Error(`Chat API error: ${response.status}`);
  }
  
  return response.json();
}

export async function getStatus(): Promise<StatusResponse> {
  const response = await fetch(`${API_BASE}/api/status`);
  
  if (!response.ok) {
    throw new Error(`Status API error: ${response.status}`);
  }
  
  return response.json();
}

export async function getToggles(): Promise<TogglesResponse> {
  const response = await fetch(`${API_BASE}/api/toggles`);
  
  if (!response.ok) {
    throw new Error(`Toggles API error: ${response.status}`);
  }
  
  return response.json();
}

export async function updateToggles(toggles: ToggleUpdate): Promise<TogglesResponse> {
  const response = await fetch(`${API_BASE}/api/toggles`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(toggles),
  });
  
  if (!response.ok) {
    throw new Error(`Toggle update API error: ${response.status}`);
  }
  
  return response.json();
}

// WebSocket connection for real-time chat
export class WebSocketClient {
  ws: WebSocket | null = null;
  reconnectAttempts = 0;
  maxReconnectAttempts = 5;
  reconnectDelay = 1000;
  onMessage: (data: any) => void;
  onError?: (error: Event) => void;
  onClose?: () => void;

  constructor(
    onMessage: (data: any) => void,
    onError?: (error: Event) => void,
    onClose?: () => void
  ) {
    this.onMessage = onMessage;
    this.onError = onError;
    this.onClose = onClose;
  }

  connect() {
    try {
      this.ws = new WebSocket(`ws://${window.location.hostname}:8000/ws/chat`);
      
      this.ws.onopen = () => {
        console.log("WebSocket connected");
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onMessage(data);
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        if (this.onError) this.onError(error);
      };

      this.ws.onclose = () => {
        console.log("WebSocket disconnected");
        if (this.onClose) this.onClose();
        this.attemptReconnect();
      };
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  send(message: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ message }));
    } else {
      console.warn("WebSocket is not connected");
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
} 