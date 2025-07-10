![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/Shubham25180/aai-dev-agent?utm_source=oss&utm_medium=github&utm_campaign=Shubham25180%2Faai-dev-agent&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)


## 🧠 The Brain: Human-Readable Structure & Explanation

### 1. How Many Pages/Files Form the "Brain"?

The "brain" of the agent is primarily composed of these files in the `agents/` directory:

- `conversational_brain.py` (main LLM/agent logic, 705 lines)
- `planner.py` (task/plan logic, 598 lines)
- `task_router.py` (task routing, 582 lines)
- `hybrid_llm_connector.py` (LLM/model connector, 465 lines)

**Total:**

- 4 main files (pages) form the core "brain" logic.
- Each file is 400–700 lines, so each is a substantial "page" of logic.

### 2. Making the Code Human-Readable

Every line or logical block in the "brain" code should be explained in plain English, right before the code. This makes the system accessible and maintainable for all developers.

**Example (applied to `nexus_gui.py`):**

```python
# This imports the PyQt6 widgets for building the GUI.
from PyQt6.QtWidgets import QApplication, QMainWindow

# This class defines the main window of the application.
class NexusMainWindow(QMainWindow):
    # ...
```

This style should be used throughout the codebase, especially in the core "brain" files.

### 3. Prompts and Model Tuning

- The `prompts/` directory contains prompt files for different models and flows:
  - `nexus_llm_brain_init.prompt`, `nexus_brain_god_tier.prompt`, `nexus_task_router.prompt`, etc.
- Each model (Stable Diffusion, DeepSeek-Coder, Open Interpreter, etc.) can have its own prompt file, which you can tune for that model's strengths and quirks.
- The code in `conversational_brain.py` loads and uses these prompts, and you can add logic to select/tune prompts per model as shown in your flowchart.

---

## 🚀 How to Run the App

### Prerequisites

- Python 3.10+
- All dependencies in `requirements.txt`
- (Optional) Ollama, ChromaDB, and other model backends as needed

### Installation

```bash
# Clone and setup
 git clone <repository>
 cd ai_dev_agent
 pip install -r requirements.txt
```

### Running the App

#### 1. Terminal (CLI) Mode

```bash
python main_simple.py
```

#### 2. GUI Mode

```bash
python gui/nexus_gui.py
```

#### 3. Run Specific Parts

- **Voice System:**
  ```bash
  python voice/voice_system.py
  ```
- **Test LLM Connection:**
  ```bash
  python test_llm_connection.py
  ```
- **Web Server (if available):**
  ```bash
  python nexus_web.py
  ```

## Running the NiceGUI Frontend

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the NiceGUI app:
   ```bash
   python main_nicegui.py
   ```

The app will launch in your browser at http://localhost:8080 with a modern ChatGPT-style interface and voice controls.

---

## 📁 What Should Be in the README

- **Project Overview:**
  - What the agent does, its personality, and its modular design.
- **Architecture:**
  - Directory structure, core components, and memory system.
- **Usage:**
  - How to install, run, and test the app (GUI, terminal, voice, web, etc.).
- **Prompts & Model Tuning:**
  - How to edit/tune prompts for different models.
- **Memory System:**
  - How core, session, and long-term memory work.
- **Human-Readable Code:**
  - Example and encouragement to comment code for clarity.
- **Troubleshooting:**
  - Common issues and solutions for LLM, voice, and GUI.
- **Contributing:**
  - How to contribute, coding style, and extensibility.
- **License:**
  - Project license and usage terms.

---

## 📝 Example: Human-Readable Code Comments

```python
# Import the typing module for type hints (Dict, Any, etc.)
from typing import Dict, Any, Optional, List

# Import datetime for timestamps and time-based logic.
from datetime import datetime
```

---

## 🤖 Prompts and Model Tuning

- Prompts are stored in the `prompts/` directory.
- Each model can have a custom prompt file for optimal performance.
- You can add logic in the agent to select the right prompt for each model/task.

---

## 🆘 Troubleshooting

- **LLM Issues:** Ensure your backend (Ollama, etc.) is running and models are available.
- **Voice Issues:** Check your OS voice configuration and `voice/` scripts.
- **GUI Issues:** Ensure PyQt6 is installed and run `gui/nexus_gui.py` directly for debugging.

---

## 🤝 Contributing

- Comment your code for human readability.
- Follow the modular structure and keep logic in the appropriate "brain" file.
- Submit issues and PRs for new features, bugfixes, or prompt improvements.

---

## 📄 License

This project is developed as a personal AI development assistant. All code and documentation are part of the nexus AI system.

---

nexus is ready to help with your coding adventures - with a side of sass! 😈🚀
