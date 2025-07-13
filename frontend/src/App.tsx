import React, { useState, useEffect, useRef } from 'react';
import { sendChatMessage, getStatus, getToggles, updateToggle, WebSocketClient, streamLLMResponse } from './nexusApi';
import type { StatusResponse, TogglesResponse } from './nexusApi';
import { Button } from "./components/ui/button";
import { Switch } from "./components/ui/switch";
import { Slider } from "./components/ui/slider";
import { GlassCard } from "./components/ui/GlassCard";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "./components/ui/tooltip";
import { Input } from "./components/ui/input";
import { cn } from "./lib/utils";
import { Info, Volume2, Bot, Send } from "lucide-react";
import { startListener, stopListener, uploadAudio } from './api/voice';
import { setMoodIntent } from './api/features';
import { useTranscriptStream } from './hooks/useTranscriptStream';
import { useProcessingStatus } from './hooks/useProcessingStatus';

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
  const chatAreaRef = useRef<HTMLDivElement>(null);
  const statusCardsRef = useRef<HTMLDivElement>(null);
  const togglesRef = useRef<HTMLDivElement>(null);
  const slidersRef = useRef<HTMLDivElement>(null);
  const footerRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    // Log chat area
    if (chatAreaRef.current) {
      console.debug('[Nexus Debug] Chat area DOM node:', chatAreaRef.current);
      console.debug('[Nexus Debug] Chat area classList:', chatAreaRef.current.className);
    } else {
      console.warn('[Nexus Debug] Chat area ref is null.');
    }
    // Log status cards
    if (statusCardsRef.current) {
      console.debug('[Nexus Debug] Status cards DOM node:', statusCardsRef.current);
      console.debug('[Nexus Debug] Status cards classList:', statusCardsRef.current.className);
    } else {
      console.warn('[Nexus Debug] Status cards ref is null.');
    }
    // Log toggles
    if (togglesRef.current) {
      console.debug('[Nexus Debug] Toggles DOM node:', togglesRef.current);
      console.debug('[Nexus Debug] Toggles classList:', togglesRef.current.className);
    } else {
      console.warn('[Nexus Debug] Toggles ref is null.');
    }
    // Log sliders
    if (slidersRef.current) {
      console.debug('[Nexus Debug] Sliders DOM node:', slidersRef.current);
      console.debug('[Nexus Debug] Sliders classList:', slidersRef.current.className);
    } else {
      console.warn('[Nexus Debug] Sliders ref is null.');
    }
    // Log footer
    if (footerRef.current) {
      console.debug('[Nexus Debug] Footer DOM node:', footerRef.current);
      console.debug('[Nexus Debug] Footer classList:', footerRef.current.className);
    } else {
      console.warn('[Nexus Debug] Footer ref is null.');
    }
    console.info('[Nexus Debug] Tailwind debug logging is active.');
  }, []);

  // Live transcript streaming
  useTranscriptStream((text) => {
    setMessages(prev => [
      ...prev,
      {
        id: Date.now().toString(),
        type: 'assistant',
        content: text,
        timestamp: new Date(),
        status: 'sent'
      }
    ]);
  });

  // Processing status spinner
  const processingStatus = useProcessingStatus();

  const handleSendMessage = async (messageToSend?: string) => {
    const message = (typeof messageToSend === 'string' ? messageToSend : inputMessage).trim();
    if (!message || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date(),
      status: 'sending'
    };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Add a placeholder assistant message for streaming
    const assistantId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, {
      id: assistantId,
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      status: 'sending'
    }]);

    try {
      let streamedContent = '';
      for await (const token of streamLLMResponse(message)) {
        streamedContent += token;
        setMessages(prev => prev.map(msg =>
          msg.id === assistantId ? { ...msg, content: streamedContent } : msg
        ));
      }
      setMessages(prev => prev.map(msg =>
        msg.id === assistantId ? { ...msg, status: 'sent' as const } : msg
      ));
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        type: 'system',
        content: 'Error streaming response: ' + (error as Error).message,
        timestamp: new Date(),
        status: 'error'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleChange = async (key: keyof TogglesResponse) => {
    if (!toggles) return;
    const newValue = !toggles[key];
    try {
      await updateToggle(key, newValue);
      setToggles(prev => prev ? { ...prev, [key]: newValue } : prev);
    } catch (error) {
      console.error('Failed to update toggle:', error);
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

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
    // Shift+Enter does nothing for single-line input, but if you switch to textarea, allow newline
  };

  // STT toggle handler
  const handleSttToggle = (v: boolean) => {
    setSttEnabled(v);
    v ? startListener() : stopListener();
  };

  // Intent/Emotion toggle handler
  const handleIntentToggle = (v: boolean) => {
    handleToggleChange('intent');
    setMoodIntent(v);
  };
  const handleEmotionToggle = (v: boolean) => {
    handleToggleChange('emotion');
    setMoodIntent(v);
  };

  // Audio upload handler
  const handleAudioUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      uploadAudio(e.target.files[0]).then(res => {
        setMessages(prev => [
          ...prev,
          {
            id: Date.now().toString(),
            type: 'assistant',
            content: res.transcript,
            timestamp: new Date(),
            status: 'sent'
          }
        ]);
      });
    }
  };

  return (
    <TooltipProvider>
      {/* TAILWIND & FONT TEST DIV - REMOVE WHEN CONFIRMED */}
      <div className="bg-red-500 text-white p-4 font-heading text-xl rounded-lg mb-4 shadow-lg">
        If this is red and uses Sora, Tailwind and fonts are working. If not, we riot.
      </div>
      {/* Add spinner for processing status */}
      {processingStatus === 'processing' && (
        <div className="fixed top-4 right-4 z-50 bg-purple-900 text-white px-4 py-2 rounded-lg shadow-lg animate-pulse">
          Processing...
        </div>
      )}
      <div className="min-h-screen bg-black text-white flex flex-col font-body">
        {/* Header */}
        <header className="w-full border-b border-purple-900 bg-black/80 px-8 py-4 flex items-center justify-between font-heading">
          <div className="flex items-center space-x-3">
            {/* Heading can be added here if needed */}
          </div>
        </header>
        {/* Main Content: 3-column grid */}
        <main className="flex-1 grid grid-cols-8 gap-6 p-8 font-body">
          {/* 1st Column: Status Cards (2/8) */}
          <div className="col-span-2 flex flex-col h-full justify-between font-heading" ref={statusCardsRef}>
            <div>
              <div className="grid grid-cols-2 gap-4">
                {/* Voice Card */}
                <GlassCard className="mb-4 bg-gradient-to-br from-purple-900 to-purple-700 shadow-xl rounded-2xl p-6 font-heading">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-purple-200 font-heading">Voice</span>
                    <div className="flex items-center gap-2">
                      <Switch checked={!!toggles?.voice} onCheckedChange={() => handleToggleChange('voice')} className="data-[state=checked]:bg-purple-500" />
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="icon-info-btn" type="button"><Info size={18} /></button>
                        </TooltipTrigger>
                      </Tooltip>
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-white mt-2">Active</div>
                  <div className="text-xs mt-1 text-purple-200">Listening</div>
                </GlassCard>
                {/* TTS Card */}
                <GlassCard className="mb-4 bg-gradient-to-br from-purple-900 to-purple-700 shadow-xl rounded-2xl p-6 font-heading">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-purple-200 font-heading">TTS</span>
                    <div className="flex items-center gap-2">
                      <Switch checked={!!toggles?.tts} onCheckedChange={() => handleToggleChange('tts')} className="data-[state=checked]:bg-purple-500" />
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="icon-info-btn" type="button"><Info size={18} /></button>
                        </TooltipTrigger>
                      </Tooltip>
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-white mt-2">edge-tts</div>
                  <div className="text-xs mt-1 text-purple-200">Ready</div>
                </GlassCard>
                {/* STT Card: update toggle */}
                <GlassCard className="mb-4 bg-gradient-to-br from-purple-900 to-purple-700 shadow-xl rounded-2xl p-6 font-heading">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-purple-200 font-heading">STT</span>
                    <div className="flex items-center gap-2">
                      <Switch checked={sttEnabled} onCheckedChange={handleSttToggle} className="data-[state=checked]:bg-purple-500" />
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="icon-info-btn" type="button"><Info size={18} /></button>
                        </TooltipTrigger>
                      </Tooltip>
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-white mt-2">Whisper</div>
                  <div className="text-xs mt-1 text-purple-200">Ready</div>
                </GlassCard>
                {/* LLM Card */}
                <GlassCard className="mb-4 bg-gradient-to-br from-purple-900 to-purple-700 shadow-xl rounded-2xl p-6 font-heading">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-purple-200 font-heading">LLM</span>
                    <div className="flex items-center gap-2">
                      <Switch checked={!!toggles?.auto_scroll} onCheckedChange={() => handleToggleChange('auto_scroll')} className="data-[state=checked]:bg-purple-500" />
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="icon-info-btn" type="button"><Info size={18} /></button>
                        </TooltipTrigger>
                      </Tooltip>
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-white mt-2">Ollama</div>
                  <div className="text-xs mt-1 text-purple-200">Connected</div>
                </GlassCard>
              </div>
              <div className="grid grid-cols-2 gap-4 mt-4">
                {/* Memory Card */}
                <GlassCard className="mb-4 bg-gradient-to-br from-purple-900 to-purple-800 shadow-xl rounded-2xl p-6 font-heading">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-purple-200 font-heading">Memory</span>
                    <div className="flex items-center gap-2">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="icon-info-btn" type="button"><Info size={18} /></button>
                        </TooltipTrigger>
                      </Tooltip>
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-white mt-2">Short: 1 | Long: N/A | Core: 2</div>
                  <div className="text-xs mt-1 text-purple-200">Editable</div>
                </GlassCard>
                {/* Agent Card */}
                <GlassCard className="mb-4 bg-gradient-to-br from-purple-900 to-purple-800 shadow-xl rounded-2xl p-6 font-heading">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-purple-200 font-heading">Agent</span>
                    <div className="flex items-center gap-2">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="icon-info-btn" type="button"><Info size={18} /></button>
                        </TooltipTrigger>
                      </Tooltip>
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-white mt-2">Processing</div>
                  <div className="text-xs mt-1 text-purple-200">Idle</div>
                </GlassCard>
                {/* GUI Card */}
                <GlassCard className="mb-4 bg-gradient-to-br from-purple-900 to-purple-800 shadow-xl rounded-2xl p-6 font-heading">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-purple-200 font-heading">GUI</span>
                    <div className="flex items-center gap-2">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="icon-info-btn" type="button"><Info size={18} /></button>
                        </TooltipTrigger>
                      </Tooltip>
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-white mt-2">Recorder: On</div>
                </GlassCard>
              </div>
            </div>
            {/* Sliders for Wit, Sarcasm, and Verbosity at the very bottom left */}
            <div className="mt-4 bg-black border-2 border-purple-700 rounded-2xl p-4 flex flex-col gap-2 shadow-lg font-body" ref={togglesRef}>
              <div className="flex items-center gap-4">
                <label htmlFor="wit-slider" className="text-sm text-purple-200 font-heading w-24">Wit:</label>
                <Slider
                  id="wit-slider"
                  value={[wit]}
                  onValueChange={(value: number[]) => setWit(value[0])}
                  max={100}
                  min={0}
                  step={1}
                  className="flex-1 accent-purple-400 h-2 rounded-lg appearance-none bg-purple-800"
                />
              </div>
              <div className="flex items-center gap-4">
                <label htmlFor="sarcasm-slider" className="text-sm text-purple-200 font-heading w-24">Sarcasm:</label>
                <Slider
                  id="sarcasm-slider"
                  value={[sarcasm]}
                  onValueChange={(value: number[]) => setSarcasm(value[0])}
                  max={100}
                  min={0}
                  step={1}
                  className="flex-1 accent-purple-300 h-2 rounded-lg appearance-none bg-purple-800"
                />
              </div>
              <div className="flex items-center gap-4">
                <label htmlFor="verbosity-slider" className="text-sm text-purple-200 font-heading w-24">Verbosity:</label>
                <Slider
                  id="verbosity-slider"
                  value={[verbosity]}
                  onValueChange={(value: number[]) => setVerbosity(value[0])}
                  max={100}
                  min={0}
                  step={1}
                  className="flex-1 accent-purple-400 h-2 rounded-lg appearance-none bg-purple-800"
                />
              </div>
            </div>
          </div>
          {/* 2nd Column: Chat Area (5/8) */}
          <div className="col-span-5 flex flex-col bg-black rounded-2xl border border-purple-900 p-6 min-h-[500px] shadow-xl font-body">
            <div className="flex-1 flex flex-col justify-end">
              {/* Chat history placeholder */}
              <div className="flex-1 flex items-center justify-center" ref={chatAreaRef}>
                <div className="bg-black/60 backdrop-blur-md rounded-2xl shadow-2xl px-8 py-6 border border-purple-700 animate-fade-in-up">
                  <span className="font-heading text-2xl text-purple-200 drop-shadow-lg">
                    "Welcome to Nexus: Where AI banter meets code brilliance. <br />
                    Your next big idea starts here."
                  </span>
                  <div className="mt-2 text-purple-400 text-sm font-body opacity-80">
                    (Chat, code, and conquer. The future is now.)
                  </div>
                </div>
              </div>
              {/* Chat input placeholder */}
              <div className="mt-4 flex items-center gap-2">
                <textarea
                  className="flex-1 bg-purple-900 border border-purple-700 rounded-lg px-4 py-2 text-white placeholder-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent font-body resize-none min-h-[40px] max-h-[120px]"
                  placeholder="Type your message or command..."
                  value={inputMessage}
                  onChange={e => setInputMessage(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage(inputMessage);
                    }
                    // Shift+Enter: allow newline (default behavior)
                  }}
                  rows={1}
                />
                <Button className="bg-purple-700 hover:bg-purple-800 text-white px-6 py-2 rounded-lg font-medium transition-colors shadow-md" onClick={() => handleSendMessage(inputMessage)}>
                  <Send size={20} />
                </Button>
              </div>
            </div>
          </div>
          {/* 3rd Column: Additional Buttons (1/8) */}
          <div className="col-span-1 flex flex-col gap-4 items-stretch font-heading">
            <Button className="bg-purple-700 hover:bg-purple-800 text-white px-4 py-2 rounded-xl font-medium transition-colors shadow-md">
              <Volume2 size={18} /> Speak
            </Button>
            <Button className="bg-purple-900 border border-purple-700 rounded-xl px-4 py-2 text-white font-medium hover:bg-purple-800 transition-colors shadow">
              <Info size={18} /> Show Last Prompt
            </Button>
            <Button className="bg-purple-900 border border-purple-700 rounded-xl px-4 py-2 text-white font-medium hover:bg-purple-800 transition-colors shadow">
              <Info size={18} /> Debug/Transparency
            </Button>
            <Button className="bg-purple-900 border border-purple-700 text-purple-300 rounded-xl px-4 py-2 font-medium hover:bg-purple-950 transition-colors shadow">
              <Info size={18} /> Pinned Facts: none
            </Button>
            {/* Toggle Switches */}
            <div className="mt-4 bg-black border-2 border-purple-700 rounded-2xl p-4 flex flex-col gap-2 shadow-lg font-body">
              <div className="flex items-center gap-2">
                <Switch checked={!!toggles?.intent} onCheckedChange={handleIntentToggle} className="data-[state=checked]:bg-purple-500" />
                <span className="text-purple-200 font-heading text-sm">Intent Detection</span>
              </div>
              <div className="flex items-center gap-2">
                <Switch checked={!!toggles?.emotion} onCheckedChange={handleEmotionToggle} className="data-[state=checked]:bg-purple-500" />
                <span className="text-purple-200 font-heading text-sm">Emotion Detection</span>
              </div>
            </div>
            {/* Audio upload input */}
            <input
              type="file"
              accept="audio/*"
              onChange={handleAudioUpload}
              className="mt-4 bg-purple-900 border border-purple-700 rounded-lg px-4 py-2 text-white"
            />
          </div>
        </main>
        {/* Footer */}
        <footer className="w-full border-t border-purple-900 bg-black/80 px-8 py-2 text-xs text-purple-400 flex items-center justify-between font-body" ref={footerRef}>
          <span>
            Voice: Active | TTS: edge-tts | STT: Whisper | LLM: Ollama | Memory: 1 short, 2 core
            <span className="ml-6">Model: <span className="text-white">Ollama</span><span className="ml-1 text-purple-400">Connected</span></span>
          </span>
          <span>© 2025 Nexus AI Dev Agent</span>
        </footer>
      </div>
    </TooltipProvider>
  );
}

export default App;
