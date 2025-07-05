import React, { useState, useEffect, useRef } from 'react';
import { sendChatMessage, getStatus, getToggles, updateToggles, WebSocketClient, StatusResponse, TogglesResponse } from './nexusApi';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
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
          ...prev.map(msg => msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg),
          {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: response.response,
            timestamp: new Date(),
            status: 'sent'
          }
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      {/* Header */}
      <header className="border-b border-gray-700 bg-gray-800/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-nexus-400 to-nexus-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">N</span>
              </div>
              <h1 className="text-xl font-sora font-semibold">Nexus AI Dev Agent</h1>
            </div>
            
            {/* Connection Status */}
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 ${wsConnected ? 'text-green-400' : 'text-red-400'}`}>
                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                <span className="text-sm font-medium">
                  {wsConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Status Panel */}
          <div className="lg:col-span-1 space-y-4">
            {/* System Status */}
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <h2 className="text-lg font-sora font-semibold mb-4">System Status</h2>
              <div className="space-y-3">
                {status && (
                  <>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-300">Memory</span>
                      <span className="text-sm">
                        {status.memory.short_term} items
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-300">Voice</span>
                      <span className={`text-sm ${getStatusColor(status.voice.status)}`}>
                        {status.voice.status}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-300">Agent</span>
                      <span className={`text-sm ${getStatusColor(status.agent.status)}`}>
                        {status.agent.status}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-300">LLM</span>
                      <span className={`text-sm ${getStatusColor(status.llm.status)}`}>
                        {status.llm.status}
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Controls */}
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <h2 className="text-lg font-sora font-semibold mb-4">Controls</h2>
              <div className="space-y-3">
                {toggles && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Voice</span>
                      <button
                        onClick={() => handleToggleChange('voice')}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          toggles.voice ? 'bg-nexus-500' : 'bg-gray-600'
                        }`}
                      >
                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          toggles.voice ? 'translate-x-6' : 'translate-x-1'
                        }`} />
                      </button>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">TTS</span>
                      <button
                        onClick={() => handleToggleChange('tts')}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          toggles.tts ? 'bg-nexus-500' : 'bg-gray-600'
                        }`}
                      >
                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          toggles.tts ? 'translate-x-6' : 'translate-x-1'
                        }`} />
                      </button>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Auto Scroll</span>
                      <button
                        onClick={() => handleToggleChange('auto_scroll')}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          toggles.auto_scroll ? 'bg-nexus-500' : 'bg-gray-600'
                        }`}
                      >
                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          toggles.auto_scroll ? 'translate-x-6' : 'translate-x-1'
                        }`} />
                      </button>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Intent Detection</span>
                      <button
                        onClick={() => handleToggleChange('intent')}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          toggles.intent ? 'bg-nexus-500' : 'bg-gray-600'
                        }`}
                      >
                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          toggles.intent ? 'translate-x-6' : 'translate-x-1'
                        }`} />
                      </button>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Emotion Detection</span>
                      <button
                        onClick={() => handleToggleChange('emotion')}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          toggles.emotion ? 'bg-nexus-500' : 'bg-gray-600'
                        }`}
                      >
                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          toggles.emotion ? 'translate-x-6' : 'translate-x-1'
                        }`} />
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-3">
            <div className="bg-gray-800/50 rounded-lg border border-gray-700 h-[600px] flex flex-col">
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-700">
                <h2 className="text-lg font-sora font-semibold">Chat with Nexus</h2>
                <p className="text-sm text-gray-400">Ask me to help with development tasks, file operations, or system automation.</p>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center text-gray-400 py-8">
                    <div className="w-16 h-16 mx-auto mb-4 bg-gray-700 rounded-full flex items-center justify-center">
                      <span className="text-2xl">🧠</span>
                    </div>
                    <p className="text-lg font-medium mb-2">Welcome to Nexus</p>
                    <p className="text-sm">I'm your AI development assistant. How can I help you today?</p>
                  </div>
                )}
                
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg px-4 py-2 ${
                        message.type === 'user'
                          ? 'bg-nexus-600 text-white'
                          : message.type === 'assistant'
                          ? 'bg-gray-700 text-white'
                          : 'bg-yellow-600/20 text-yellow-200'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{message.content}</div>
                      <div className="text-xs text-gray-400 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                        {message.status === 'sending' && ' • Sending...'}
                        {message.status === 'error' && ' • Error'}
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-700 rounded-lg px-4 py-2">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                        <span className="text-sm text-gray-400">Nexus is thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-4 border-t border-gray-700">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Type your message or command..."
                    className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-nexus-500 focus:border-transparent"
                    disabled={isLoading}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={isLoading || !inputMessage.trim()}
                    className="bg-nexus-600 hover:bg-nexus-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg font-medium transition-colors"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
