# 🧠 NOVA AI Development Assistant

**Your Intelligent, Conversational AI Development Friend**

NOVA is a real-time, memory-aware AI development assistant that acts like a friend who remembers everything and intelligently routes tasks to specialized models. Built for speed, privacy, and natural conversation.

## 🎯 What NOVA Does

NOVA is your AI development buddy that:

1. **🎤 Listens** - Processes voice commands in real-time (English, Hindi, Indian English)
2. **🧠 Thinks** - Analyzes your intent and breaks tasks into atomic steps
3. **🔄 Routes** - Intelligently selects the right specialized model for each task
4. **💾 Remembers** - Maintains persistent memory of conversations and preferences
5. **⚡ Responds** - Provides fast, friendly responses with real-time performance

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Voice Input   │───▶│  Fast Voice     │───▶│   NOVA Brain    │
│   (Speech)      │    │   System        │    │   (Intelligence)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Memory        │    │   Task Router   │
                       │   Manager       │    │   & Executor    │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Specialized   │    │   Voice Output  │
                       │   Models        │    │   (TTS)         │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Key Features

### ⚡ Real-Time Performance

- **Chunked Audio Processing** (3-second windows)
- **Voice Activity Detection** (VAD) for efficiency
- **Async Processing Pipeline** for non-blocking operation
- **Response Caching** for faster repeated queries
- **Optimized Models** (Whisper base.en, quantized LLMs)

### 🧠 Intelligent Task Routing

- **Intent Detection** - Understands what you want to do
- **Model Selection** - Routes to the right specialist:
  - `code_generator` - Create new code
  - `code_reviewer` - Analyze and debug code
  - `file_manager` - File operations
  - `git_manager` - Version control
  - `test_runner` - Testing and validation
  - `conversation_agent` - General chat

### 💾 Persistent Memory

- **Short-term Memory** - Current session context
- **Long-term Memory** - User preferences and patterns
- **Core Behavior** - Personality and interaction style
- **Automatic Persistence** - Everything is saved automatically

### 🌍 Multi-Language Support

- **English** - Primary language
- **Hindi** - Native Hindi commands
- **Indian English** - Optimized for Indian accents
- **Auto-detection** - Switches languages automatically

## 📦 System Components

### 1. NOVA Brain (`agents/nova_brain.py`)

The core intelligence that:

- Processes user input (voice/text)
- Analyzes intent and complexity
- Generates friendly, natural responses
- Manages conversation flow
- Maintains memory context

### 2. Fast Voice System (`voice/fast_voice_system.py`)

Optimized for real-time performance:

- Chunked audio processing
- Voice Activity Detection
- Fast Whisper models
- Streaming TTS response
- Async processing pipeline

### 3. Task Router (`agents/task_router.py`)

Intelligent task classification and routing:

- Pattern-based task detection
- Complexity assessment
- Model selection
- Prompt optimization
- Performance tracking

### 4. Memory Manager (`memory/memory_manager.py`)

Comprehensive memory system:

- Short-term session memory
- Long-term persistent memory
- Core behavior patterns
- Automatic persistence
- Memory search and retrieval

### 5. LLM Connector (`agents/llm_connector.py`)

Model-agnostic LLM interface:

- Support for multiple providers (Ollama, OpenAI, HuggingFace)
- Retry logic and error handling
- Response caching
- Performance optimization

## 🎮 Usage Examples

### Voice Commands

```bash
# Basic interaction
"Hello Nova!"
"What can you help me with?"

# Code generation
"Create a Python function to calculate fibonacci numbers"
"Write a React component for a todo list"

# Code review
"Review this code: def add(a, b): return a + b"
"Check for bugs in my authentication module"

# File operations
"Open the main.py file"
"Create a new folder called utils"

# Git operations
"Commit my changes to git"
"Push to the remote repository"

# Testing
"Run the test suite"
"Create unit tests for the user service"

# System operations
"Install Node.js on my system"
"Start the development server"
```

### Text Commands

Same commands work via text input for when voice isn't available or preferred.

## ⚙️ Configuration

### Basic Configuration

```yaml
model:
  provider: "ollama"
  model_name: "mistral:7b-instruct"
  endpoint: "http://localhost:11434"
  max_tokens: 1000
  temperature: 0.7

voice:
  enabled: true
  model_size: "base.en" # Fastest for English
  device: "cpu"
  compute_type: "int8"
  tts_engine: "pyttsx3"
  chunk_duration: 3.0
  vad_threshold: 0.5

paths:
  memory: "memory"
  logs: "logs"
  undo: "undo"

performance:
  cache_responses: true
  max_cache_size: 100
  memory_update_interval: 30
  max_conversation_history: 50
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Ollama (for local LLM)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Mistral model
ollama pull mistral:7b-instruct
```

### 3. Run the System

```bash
# Test the complete system
python test_nova_system.py

# Run the main application
python main.py
```

### 4. Start Using NOVA

```bash
# Say "Hello Nova!" to start
# Use voice commands for hands-free development
# NOVA remembers everything and learns your preferences
```

## 📊 Performance Metrics

### Speed Improvements

- **Traditional Pipeline**: ~3-5 seconds
- **NOVA Pipeline**: ~0.5-1 second
- **Speed Improvement**: 3-5x faster

### Optimization Techniques

- **Chunked Audio Processing** - Process audio in 3-second windows
- **Voice Activity Detection** - Skip silence processing
- **Response Caching** - Cache repeated queries
- **Async Processing** - Non-blocking operations
- **Quantized Models** - Faster inference with minimal quality loss

## 🔧 Development

### Project Structure

```
ai_dev_agent/
├── agents/
│   ├── nova_brain.py          # Core intelligence
│   ├── task_router.py         # Task classification
│   ├── llm_connector.py       # LLM interface
│   └── conversational_brain.py # Legacy brain
├── voice/
│   ├── fast_voice_system.py   # Optimized voice processing
│   ├── voice_system.py        # Legacy voice system
│   ├── recognizer.py          # Speech recognition
│   └── responder.py           # Text-to-speech
├── memory/
│   └── memory_manager.py      # Memory management
├── utils/
│   └── logger.py              # Logging utilities
├── test_nova_system.py        # Complete system test
├── main.py                    # Main application
└── requirements.txt           # Dependencies
```

### Testing

```bash
# Test individual components
python test_nova_system.py

# Test voice system
python test_voice.py

# Test memory system
python test_memory.py
```

## 🎯 Use Cases

### For Developers

- **Hands-free coding** - Voice commands while coding
- **Code generation** - Create functions, classes, modules
- **Code review** - Analyze and debug code
- **File management** - Navigate and organize files
- **Git operations** - Version control commands
- **Testing** - Run tests and create test cases

### For Teams

- **Pair programming** - Natural conversation with AI
- **Code documentation** - Generate docs and comments
- **Project setup** - Initialize new projects
- **Dependency management** - Install and update packages
- **Deployment** - Deploy applications

### For Learning

- **Code explanation** - Understand complex code
- **Best practices** - Learn coding standards
- **Debugging help** - Find and fix issues
- **Architecture guidance** - Design system architecture

## 🔒 Privacy & Security

- **Local Processing** - All processing happens locally
- **No External APIs** - No data sent to external services
- **Memory Encryption** - Sensitive data is encrypted
- **Audit Logging** - All actions are logged for transparency
- **User Control** - Full control over what NOVA can do

## 🛠️ Customization

### Adding New Models

```python
# Add new model in llm_connector.py
def _send_custom_model(self, prompt: str, **kwargs):
    # Your custom model implementation
    pass
```

### Adding New Task Types

```python
# Add new task pattern in task_router.py
'custom_task': {
    'keywords': ['custom', 'task', 'keywords'],
    'patterns': [r'custom\s+pattern'],
    'model': 'custom_model',
    'priority': 'medium'
}
```

### Custom Voice Commands

```python
# Add custom commands in voice/commands.py
CUSTOM_COMMANDS = {
    'custom_command': {
        'pattern': r'custom\s+command',
        'action': 'custom_action',
        'description': 'Custom command description'
    }
}
```

## 📈 Roadmap

### Phase 1: Core System ✅

- [x] NOVA Brain implementation
- [x] Fast voice system
- [x] Memory management
- [x] Task routing
- [x] Basic voice commands

### Phase 2: Advanced Features 🚧

- [ ] Advanced code generation
- [ ] Multi-file operations
- [ ] Project templates
- [ ] Advanced debugging
- [ ] Performance profiling

### Phase 3: Integration 🎯

- [ ] IDE plugins (VS Code, PyCharm)
- [ ] CI/CD integration
- [ ] Cloud deployment
- [ ] Team collaboration
- [ ] Advanced analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI Whisper** - Speech recognition
- **Ollama** - Local LLM hosting
- **Mistral AI** - Language model
- **Python Community** - Various libraries and tools

---

**NOVA - Your AI Development Friend** 🧠✨

_Remember everything, understand anything, help with everything._
