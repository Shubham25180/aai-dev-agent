# Manual n8n Workflow Setup Guide

Since the JSON import is having issues, here's how to create the workflows manually in n8n.

## 1. Voice Command Workflow

### Step 1: Create New Workflow
1. Open n8n at `http://localhost:5678`
2. Click "Add workflow"
3. Name it "Voice Command Workflow"

### Step 2: Add Webhook Node
1. Click the "+" to add a node
2. Search for "Webhook"
3. Select "Webhook" node
4. Configure:
   - **HTTP Method**: POST
   - **Path**: `voice-command`
   - **Response Mode**: Respond to Webhook

### Step 3: Add Execute Command Node
1. Click the "+" to add another node
2. Search for "Execute Command"
3. Select "Execute Command" node
4. Configure:
   - **Command**: `python`
   - **Arguments**: `scripts/voice_handler.py --input "{{$json.user_input}}" --action "process" --output-format json`

### Step 4: Connect Nodes
1. Connect the Webhook node to the Execute Command node
2. Connect the Execute Command node to the Webhook Response node

### Step 5: Activate
1. Click the toggle in the top-right to activate the workflow
2. Save the workflow

## 2. GUI Automation Workflow

### Step 1: Create New Workflow
1. Click "Add workflow"
2. Name it "GUI Automation Workflow"

### Step 2: Add Webhook Node
1. Add Webhook node
2. Configure:
   - **HTTP Method**: POST
   - **Path**: `gui-action`

### Step 3: Add Execute Command Node
1. Add Execute Command node
2. Configure:
   - **Command**: `python`
   - **Arguments**: `scripts/gui_automation.py --action "{{$json.action}}" --coords "{{$json.coords}}" --output-format json`

### Step 4: Connect and Activate
1. Connect Webhook → Execute Command → Webhook Response
2. Activate the workflow

## 3. Code Generation Workflow

### Step 1: Create New Workflow
1. Click "Add workflow"
2. Name it "Code Generation Workflow"

### Step 2: Add Webhook Node
1. Add Webhook node
2. Configure:
   - **HTTP Method**: POST
   - **Path**: `generate-code`

### Step 3: Add Execute Command Node
1. Add Execute Command node
2. Configure:
   - **Command**: `python`
   - **Arguments**: `scripts/code_generator.py --prompt "{{$json.prompt}}" --language "{{$json.language}}" --output-format json`

### Step 4: Connect and Activate
1. Connect Webhook → Execute Command → Webhook Response
2. Activate the workflow

## Testing the Workflows

Once all workflows are created and activated, test them:

### Test Voice Command
```bash
curl -X POST http://localhost:5678/webhook/voice-command \
  -H "Content-Type: application/json" \
  -d '{"user_input": "test voice input"}'
```

### Test GUI Automation
```bash
curl -X POST http://localhost:5678/webhook/gui-action \
  -H "Content-Type: application/json" \
  -d '{"action": "click", "coords": "100,200"}'
```

### Test Code Generation
```bash
curl -X POST http://localhost:5678/webhook/generate-code \
  -H "Content-Type: application/json" \
  -d '{"prompt": "create a function", "language": "python"}'
```

## PowerShell Testing (Windows)

### Test Voice Command
```powershell
Invoke-WebRequest -Uri "http://localhost:5678/webhook/voice-command" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"user_input": "test voice input"}'
```

### Test GUI Automation
```powershell
Invoke-WebRequest -Uri "http://localhost:5678/webhook/gui-action" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"action": "click", "coords": "100,200"}'
```

### Test Code Generation
```powershell
Invoke-WebRequest -Uri "http://localhost:5678/webhook/generate-code" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"prompt": "create a function", "language": "python"}'
```

## Troubleshooting

### Workflow Not Found
- Make sure the workflow is activated (toggle in top-right)
- Check the webhook path matches exactly
- Verify the workflow is saved

### Python Script Not Found
- Make sure you're in the correct directory
- Check that scripts are executable
- Verify the script path is correct

### Command Execution Failed
- Check n8n logs for error details
- Verify Python is in PATH
- Test the script manually first

## Next Steps

After creating the workflows:
1. Test each workflow individually
2. Run the integration test: `python test_n8n_integration.py`
3. Add webhook calls to your GUI
4. Create more complex workflows as needed 