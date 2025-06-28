# 🤖 AI Dev Agent - NOVA System

A memory-aware, undo-capable, proactive AI developer assistant with voice support and hybrid LLM integration.

## 🚀 Features

### Core Capabilities

- **🧠 Conversational Brain**: Intelligent task processing with dual-model strategy
- **🎤 Voice Integration**: Multi-language voice commands (English & Hindi)
- **💾 Memory Management**: Persistent context and conversation history
- **↩️ Undo System**: Safe operation with rollback capabilities
- **⚡ Speed Optimizations**: Hybrid LLM routing for optimal performance

### LLM Integration

- **🔄 Hybrid Backend**: Ollama for coding, Hugging Face for speed testing
- **🧠 Multiple Models**: Support for various model sizes and configurations
- **⚡ Intelligent Routing**: Automatic backend selection based on task type
- **📊 Performance Monitoring**: Detailed speed and memory metrics

### Voice System

- **🌍 Multi-language**: English and Hindi voice recognition
- **🎯 Command Processing**: Natural language to action mapping
- **⚡ Real-time**: Continuous listening with low latency
- **🔊 Text-to-Speech**: Voice responses and feedback

## 🏗️ Architecture

```
AI Dev Agent/
├── agents/                 # Core AI components
│   ├── conversational_brain.py
│   ├── hybrid_llm_connector.py
│   ├── huggingface_connector.py
│   └── llm_connector.py
├── app/                   # Application layer
│   ├── bootstrap.py
│   ├── controller.py
│   └── router.py
├── voice/                 # Voice processing
│   ├── voice_system.py
│   ├── enhanced_voice_system.py
│   └── commands.py
├── executor/              # Task execution
│   ├── code_editor.py
│   ├── file_ops.py
│   └── shell_ops.py
├── memory/                # Memory management
│   └── memory_manager.py
├── undo/                  # Undo system
│   └── undo_manager.py
└── config/                # Configuration files
    ├── settings.yaml
    ├── settings_hybrid.yaml
    └── settings_huggingface.yaml
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ai-dev-agent.git
cd ai-dev-agent

# Install dependencies
pip install -r requirements.txt

# For Hugging Face integration
pip install -r requirements_huggingface.txt
```

### Configuration

```bash
# Use hybrid configuration (recommended)
cp config/settings_hybrid.yaml config/settings.yaml

# Or use Hugging Face only
cp config/settings_huggingface.yaml config/settings.yaml
```

### Running

```bash
# Start the AI Dev Agent
python main.py

# Run speed tests
python test_hybrid_speed.py
python test_huggingface_speed.py
```

## 🧠 Hybrid LLM System

### Backend Selection

| Task Type            | Backend      | Use Case                                |
| -------------------- | ------------ | --------------------------------------- |
| **Coding**           | Ollama       | Code generation, debugging, refactoring |
| **Simple Q&A**       | Hugging Face | Quick responses, voice commands         |
| **Complex Analysis** | Ollama       | Detailed reasoning, problem solving     |
| **Speed Testing**    | Hugging Face | Performance comparison, optimization    |

### Model Configurations

```yaml
# Ollama (Coding Tasks)
ollama:
  model_name: "deepseek-coder-v2:lite"
  temperature: 0.3
  max_tokens: 2048

# Hugging Face (Speed Tasks)
huggingface:
  models:
    fast:
      model_name: "microsoft/DialoGPT-small"
      max_tokens: 512
    balanced:
      model_name: "microsoft/DialoGPT-medium"
      max_tokens: 1024
```

## 🎤 Voice Commands

### English Commands

- "Open main.py"
- "Create new function"
- "Run tests"
- "Save all files"
- "Undo last action"

### Hindi Commands

- "file kholo"
- "function banane ke liye"
- "test run karo"
- "sab files save karo"
- "last action undo karo"

## 📊 Performance

### Speed Test Results

- **Ollama (Coding)**: ~0.5-1.0s response time
- **Hugging Face (Simple)**: ~0.2-0.3s response time
- **Voice Processing**: ~0.1-0.2s latency
- **Memory Usage**: 200MB-1.5GB depending on model

### Optimization Features

- **Prompt Caching**: 90%+ cache hit rate for repeated requests
- **Model Quantization**: 8-bit models for faster inference
- **Lazy Loading**: Models loaded on demand
- **Health Monitoring**: Automatic fallback and recovery

## 🔧 Configuration

### Hybrid Configuration

```yaml
llm:
  model_type: "hybrid"
  routing:
    default_backend: "ollama"
    coding_keywords: ["code", "function", "debug", "refactor"]
    simple_keywords: ["hello", "what is", "explain briefly"]
```

### Voice Configuration

```yaml
voice:
  enabled: true
  model_size: "base.en"
  supported_languages: ["en", "hi"]
  min_confidence: 0.6
```

## 🧪 Testing

### Speed Tests

```bash
# Test hybrid system
python test_hybrid_speed.py

# Test Hugging Face only
python test_huggingface_speed.py

# Test voice system
python test_voice.py
```

### Performance Monitoring

```python
from agents.hybrid_llm_connector import HybridLLMConnector

connector = HybridLLMConnector(config)
metrics = connector.get_performance_metrics()
print(f"Cache hit rate: {metrics['cache_hit_rate']:.1%}")
print(f"Average response time: {metrics['avg_response_time']:.3f}s")
```

## 📈 Roadmap

- [ ] **Advanced Code Analysis**: AST-based code understanding
- [ ] **Multi-modal Support**: Image and video processing
- [ ] **Collaborative Features**: Team development support
- [ ] **Plugin System**: Extensible architecture
- [ ] **Cloud Integration**: Remote model serving

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama**: For local model serving
- **Hugging Face**: For model hosting and optimization
- **Whisper**: For voice recognition
- **OpenAI**: For inspiration and best practices

---

**Made with ❤️ by Shubham25180**

_Your AI Development Companion_
