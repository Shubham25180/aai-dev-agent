import React, { useState, useEffect, useRef } from 'react';
import { sendChatMessage, getStatus, getToggles, updateToggles, WebSocketClient } from './nexusApi';
import type { StatusResponse, TogglesResponse } from './nexusApi';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
}

// Placeholder status card components
const StatusCard = ({ title, value, status, toggle }: { title: string; value: string; status?: string; toggle?: React.ReactNode }) => (
  <div className="bg-gray-800 rounded-lg p-4 flex flex-col items-start border border-gray-700 min-w-[140px]">
    <div className="flex items-center w-full justify-between">
      <div className="text-xs text-gray-400 mb-1">{title}</div>
      {toggle && <div className="ml-2">{toggle}</div>}
    </div>
    <div className="text-lg font-semibold text-white">{value}</div>
    {status && <div className="text-xs mt-1 text-gray-400">{status}</div>}
  </div>
);

function ToggleSwitch({ label, checked, onChange }: { label: string; checked: boolean; onChange: () => void }) {
  return (
    <label className="flex items-center gap-3 cursor-pointer select-none">
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={onChange}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 focus:outline-none ${checked ? 'bg-blue-600' : 'bg-gray-400'}`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform duration-200 ${checked ? 'translate-x-5' : 'translate-x-1'}`}
        />
      </button>
      <span className="text-sm text-gray-200 min-w-[120px]">{label}</span>
    </label>
  );
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [toggles, setToggles] = useState<TogglesResponse | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [wsClient, setWsClient] = useState<WebSocketClient | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [wit, setWit] = useState(50);
  const [sarcasm, setSarcasm] = useState(50);
  const [verbosity, setVerbosity] = useState(50);
  const [sttEnabled, setSttEnabled] = useState(true);

  // Initialize WebSocket connection
  useEffect(() => {
    const client = new WebSocketClient(
      (data) => {
        // Handle incoming WebSocket messages
        if (data.type === 'chat_response') {
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            type: 'assistant',
            content: data.message,
            timestamp: new Date(),
            status: 'sent'
          }]);
        } else if (data.type === 'status_update') {
          setStatus(data.status);
        }
      },
      (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      },
      () => {
        setWsConnected(false);
      }
    );

    client.connect();
    setWsClient(client);
    setWsConnected(true);

    return () => {
      client.disconnect();
    };
  }, []);

  // Load initial status and toggles
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [statusData, togglesData] = await Promise.all([
          getStatus(),
          getToggles()
        ]);
        setStatus(statusData);
        setToggles(togglesData);
      } catch (error) {
        console.error('Failed to load initial data:', error);
      }
    };

    loadInitialData();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
      status: 'sending'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Try WebSocket first, fallback to REST
      if (wsClient && wsConnected) {
        wsClient.send(inputMessage);
        setMessages(prev => prev.map(msg => 
          msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg
        ));
      } else {
        // Fallback to REST API
        const response = await sendChatMessage(inputMessage);
        setMessages(prev => [
          ...prev.map(msg => msg.id === userMessage.id ? { ...msg, status: 'sent' as 'sent' } : msg),
          {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: response.response,
            timestamp: new Date(),
            status: 'sent'
          } satisfies ChatMessage
        ]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id ? { ...msg, status: 'error' } : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleChange = async (key: keyof TogglesResponse) => {
    if (!toggles) return;

    const newToggles = { ...toggles, [key]: !toggles[key] };
    setToggles(newToggles);

    try {
      await updateToggles({ [key]: newToggles[key] });
    } catch (error) {
      console.error('Failed to update toggle:', error);
      // Revert on error
      setToggles(toggles);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'connected':
      case 'processing':
        return 'text-green-400';
      case 'inactive':
      case 'disconnected':
        return 'text-red-400';
      default:
        return 'text-yellow-400';
    }
  };

  // Add a handler for the Speak button
  const handleSpeak = () => {
    // Placeholder: This should call the backend to speak the last prompt using edge-tts or fallback
    // For now, just log to console
    if (messages.length > 0) {
      const lastPrompt = messages[messages.length - 1].content;
      console.log('Speak:', lastPrompt);
      // TODO: Call backend TTS endpoint with lastPrompt
    } else {
      console.log('No prompt to speak.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-950 to-black text-white flex flex-col">
      {/* Header */}
      <header className="w-full border-b border-gray-800 bg-gray-900/80 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {/* Removed the main heading for a test/dev layout */}
        </div>
        {/* Removed the model info from header */}
      </header>

      {/* Main Content: 3-column grid */}
      <main className="flex-1 grid grid-cols-8 gap-6 p-8">
        {/* 1st Column: Status Cards (2/8) */}
        <div className="col-span-2 flex flex-col h-full justify-between">
          <div>
            <div className="grid grid-cols-2 gap-4">
              <StatusCard
                title="Voice"
                value="Active"
                status="Listening"
                toggle={<ToggleSwitch label="" checked={!!toggles?.voice} onChange={() => handleToggleChange('voice')} />}
              />
              <StatusCard
                title="TTS"
                value="edge-tts"
                status="Ready"
                toggle={<ToggleSwitch label="" checked={!!toggles?.tts} onChange={() => handleToggleChange('tts')} />}
              />
              <StatusCard
                title="STT"
                value="Whisper"
                status="Ready"
                toggle={<ToggleSwitch label="" checked={sttEnabled} onChange={() => setSttEnabled(v => !v)} />}
              />
              <StatusCard title="LLM" value="Ollama" status="Connected" />
            </div>
            <div className="grid grid-cols-2 gap-4 mt-4">
              <StatusCard title="Memory" value="Short: 1 | Long: N/A | Core: 2" status="Editable" />
              <StatusCard title="Agent" value="Processing" status="Idle" />
              <StatusCard title="GUI" value="Recorder: On" status="" />
              <div />
            </div>
          </div>

          {/* Sliders for Wit, Sarcasm, and Verbosity at the very bottom left */}
          <div className="flex flex-col gap-2 bg-gray-900 border border-gray-700 rounded-lg p-4 mt-4">
            <div className="flex items-center gap-4">
              <label htmlFor="wit-slider" className="text-sm text-gray-300 w-24">Wit:</label>
              <input
                id="wit-slider"
                type="range"
                min={0}
                max={100}
                value={wit}
                onChange={e => setWit(Number(e.target.value))}
                className="flex-1 accent-green-600 h-2 rounded-lg appearance-none bg-gray-700"
              />
            </div>
            <div className="flex items-center gap-4">
              <label htmlFor="sarcasm-slider" className="text-sm text-gray-300 w-24">Sarcasm:</label>
              <input
                id="sarcasm-slider"
                type="range"
                min={0}
                max={100}
                value={sarcasm}
                onChange={e => setSarcasm(Number(e.target.value))}
                className="flex-1 accent-blue-400 h-2 rounded-lg appearance-none bg-gray-700"
              />
            </div>
            <div className="flex items-center gap-4">
              <label htmlFor="verbosity-slider" className="text-sm text-gray-300 w-24">Verbosity:</label>
              <input
                id="verbosity-slider"
                type="range"
                min={0}
                max={100}
                value={verbosity}
                onChange={e => setVerbosity(Number(e.target.value))}
                className="flex-1 accent-green-600 h-2 rounded-lg appearance-none bg-gray-700"
              />
            </div>
          </div>
        </div>

        {/* 2nd Column: Chat Area (5/8) */}
        <div className="col-span-5 flex flex-col bg-gray-900 rounded-lg border border-gray-800 p-6 min-h-[500px]">
          <div className="flex-1 flex flex-col justify-end">
            {/* Chat history placeholder */}
            <div className="flex-1 text-gray-400 flex items-center justify-center">
              <span>Chat area (GPT-style) coming soon...</span>
            </div>
            {/* Chat input placeholder */}
            <div className="mt-4 flex items-center gap-2">
              <input
                type="text"
                className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-nexus-500 focus:border-transparent"
                placeholder="Type your message or command..."
                disabled
              />
              <button className="bg-nexus-600 hover:bg-nexus-700 text-white px-6 py-2 rounded-lg font-medium transition-colors" disabled>
                Send
              </button>
            </div>
          </div>
        </div>

        {/* 3rd Column: Additional Buttons (1/8) */}
        <div className="col-span-1 flex flex-col gap-4 items-stretch">
          <button
            className="bg-blue-700 border border-blue-800 rounded-lg px-4 py-2 text-white font-medium hover:bg-blue-800 transition-colors"
            onClick={handleSpeak}
          >
            Speak
          </button>
          <button className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white font-medium hover:bg-gray-700 transition-colors">Show Last Prompt</button>
          <button className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white font-medium hover:bg-gray-700 transition-colors">Debug/Transparency</button>
          <button className="bg-gray-800 border border-blue-700 text-blue-400 rounded-lg px-4 py-2 font-medium hover:bg-blue-900 transition-colors">Pinned Facts: none</button>

          {/* Toggle Switches */}
          <div className="mt-4 bg-gray-900 border-2 border-blue-500 rounded-lg p-4 flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <ToggleSwitch
                label="Auto-scroll Chat"
                checked={!!toggles?.auto_scroll}
                onChange={() => handleToggleChange('auto_scroll')}
              />
            </div>
            <div className="flex items-center gap-2">
              <ToggleSwitch
                label="Intent Detection"
                checked={!!toggles?.intent}
                onChange={() => handleToggleChange('intent')}
              />
            </div>
            <div className="flex items-center gap-2">
              <ToggleSwitch
                label="Emotion Detection"
                checked={!!toggles?.emotion}
                onChange={() => handleToggleChange('emotion')}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-gray-800 bg-gray-900/80 px-8 py-2 text-xs text-gray-400 flex items-center justify-between">
        <span>
          Voice: Active | TTS: edge-tts | STT: Whisper | LLM: Ollama | Memory: 1 short, 2 core
          <span className="ml-6">Model: <span className="text-white">Ollama</span><span className="ml-1 text-green-400">Connected</span></span>
        </span>
        <span>© 2025 Nexus AI Dev Agent</span>
      </footer>
    </div>
  );
}

export default App;
