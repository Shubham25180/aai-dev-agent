# AI Dev Agent

A memory-aware, undo-capable, proactive AI developer assistant. Modular, extensible, and ready for CLI, GUI, and voice workflows.

## Folder Structure

```
ai_dev_agent/
├── main.py                        # Entry point
├── requirements.txt               # Dependencies
├── README.md
├── config/
│   └── settings.yaml              # Paths, feature flags, default models, OS mode
├── app/
│   ├── controller.py              # Controls flow between input → plan → execute
│   ├── router.py                  # Routes tasks to appropriate modules
│   └── bootstrap.py               # Initializes memory, config, models
├── agents/
│   ├── planner.py                 # Breaks high-level tasks into steps
│   ├── prompt_template.py         # System prompts and dynamic builders
│   └── llm_connector.py           # Interface to Hugging Face, Ollama, or OpenAI
├── memory/
│   ├── short_term.json            # Per-session memory (active)
│   ├── long_term.json             # Summary of major actions
│   ├── core_behavior.json         # Tracks patterns/preferences
│   └── embeddings/
│       └── index.pkl
├── logs/
│   ├── plans/
│   ├── actions/
│   ├── sessions/
│   ├── errors/
│   └── speech/
├── executor/
│   ├── file_ops.py
│   ├── code_editor.py
│   ├── shell_ops.py
│   └── gui_ops.py
├── undo/
│   ├── snapshot_store.py
│   ├── undo_manager.py
│   └── history.json
├── voice/
│   ├── recognizer.py
│   ├── responder.py
│   └── commands.py
├── utils/
│   ├── os_utils.py
│   ├── logger.py
│   └── tokenizer.py
```

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Edit `config/settings.yaml` for your environment.
3. Run: `python main.py`

---

## Assistant Action Logging
**important"add it to current memory"
All actions performed by the AI assistant(cursor ide ai) (such as file creation, edits, and project scaffolding) are logged for full traceability and auditability.

- **Log file location:** `logs/actions/assistant_actions_log.json`
- **What is recorded:**
  - Timestamp of each action
  - Action type (e.g., create_file, edit_file)
  - File(s) affected
  - Description of the action
- This log enables you to review, audit, and potentially undo any step taken by the assistant.

---

- Modular: Add new agents, executors, or memory backends easily.
- Extensible: CLI, GUI, and voice support.
- Safe: Undo/rollback for every action. 