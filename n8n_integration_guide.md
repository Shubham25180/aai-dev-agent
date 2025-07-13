# N8N Integration Guide for NEXUS AI Agent

## Overview

This guide shows how to integrate n8n workflows with your existing Python codebase for visual debugging and workflow orchestration.

## Architecture

```
n8n Webhook → Python Script → Your Existing Modules
     ↓              ↓              ↓
Visual Debug    Command Line    ActionRouter, LLMPlanner, Executor
```

## Setup

### 1. Install n8n
```bash
npm install n8n -g
n8n start
```

### 2. Create Scripts Directory
```bash
mkdir scripts
```

### 3. Make Scripts Executable
```bash
chmod +x scripts/*.py
```

## Available Scripts

### Voice Handler (`scripts/voice_handler.py`)
```bash
python scripts/voice_handler.py --input "user voice input" --action "process"
```

### GUI Automation (`scripts/gui_automation.py`)
```bash
python scripts/gui_automation.py --action "click" --coords "100,200"
python scripts/gui_automation.py --action "type" --text "hello world"
python scripts/gui_automation.py --action "custom" --intent "click the button"
```

### Code Generator (`scripts/code_generator.py`)
```bash
python scripts/code_generator.py --prompt "create a function" --language "python" --file-path "output.py"
```

## n8n Workflows

### 1. Voice Command Workflow
- **Webhook**: `POST /voice-command`
- **Input**: `{"user_input": "click the button"}`
- **Output**: `{"status": "success", "response": "..."}`

### 2. GUI Automation Workflow
- **Webhook**: `POST /gui-action`
- **Input**: `{"action": "click", "coords": "100,200"}`
- **Output**: `{"status": "success", "action": "click", "coords": [100, 200]}`

### 3. Code Generation Workflow
- **Webhook**: `POST /generate-code`
- **Input**: `{"prompt": "create a function", "language": "python", "file_path": "output.py"}`
- **Output**: `{"status": "success", "generated_code": "..."}`

## Usage Examples

### From Your GUI
```python
# In nexus_gui.py - add this method
def send_to_n8n(self, workflow_type, data):
    """Send data to n8n workflow"""
    import requests
    
    webhook_urls = {
        'voice': 'http://localhost:5678/webhook/voice-command',
        'gui': 'http://localhost:5678/webhook/gui-action',
        'code': 'http://localhost:5678/webhook/generate-code'
    }
    
    try:
        response = requests.post(webhook_urls[workflow_type], json=data)
        return response.json()
    except Exception as e:
        self.status_panel.add_log(f"n8n error: {e}", "ERROR")
        return None
```

### From Command Line
```bash
# Test voice processing
curl -X POST http://localhost:5678/webhook/voice-command \
  -H "Content-Type: application/json" \
  -d '{"user_input": "click the button"}'

# Test GUI automation
curl -X POST http://localhost:5678/webhook/gui-action \
  -H "Content-Type: application/json" \
  -d '{"action": "click", "coords": "100,200"}'

# Test code generation
curl -X POST http://localhost:5678/webhook/generate-code \
  -H "Content-Type: application/json" \
  -d '{"prompt": "create a function", "language": "python"}'
```

## Benefits

### 1. Visual Debugging
- See exactly which node executed
- View input/output for each step
- Track execution time
- Debug failed nodes

### 2. Workflow Reusability
- Save complex workflows
- Share workflows with team
- Version control workflows
- Import/export functionality

### 3. Error Handling
- Built-in retry logic
- Error notifications
- Conditional execution
- Fallback paths

### 4. Solo Developer Friendly
- No API complexity
- Direct Python script calls
- JSON input/output
- Easy to extend

## Integration with Existing Code

### Your Current Flow
```
User Input → ConversationalBrain → ActionRouter → Executor
```

### With n8n Integration
```
User Input → n8n Workflow → Python Script → ActionRouter → Executor
```

### What Stays the Same
- All your existing Python modules
- Your GUI interface
- Your voice system
- Your LLM connectors

### What Gets Added
- n8n workflow orchestration
- Visual debugging interface
- Workflow versioning
- Error handling improvements

## Next Steps

1. **Start Simple**: Use n8n for one workflow type first
2. **Add Gradually**: Migrate workflows one by one
3. **Customize**: Add your own Python scripts as needed
4. **Extend**: Create complex multi-step workflows

## Troubleshooting

### Script Not Found
```bash
# Make sure scripts are executable
chmod +x scripts/*.py

# Check Python path
python scripts/voice_handler.py --help
```

### n8n Not Starting
```bash
# Check if port 5678 is available
netstat -an | grep 5678

# Start n8n on different port
n8n start --port 5679
```

### Permission Issues
```bash
# Run n8n with proper permissions
sudo n8n start

# Or run as user
n8n start --user
```

## Conclusion

This approach gives you:
- **Visual debugging** without API complexity
- **Workflow reusability** for common tasks
- **Easy extension** with new Python scripts
- **Zero disruption** to existing code

Your `main.py` stays exactly the same, and you get powerful workflow orchestration with visual debugging. 