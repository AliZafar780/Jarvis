# 🤖 Jarvis - AI Agent with Ollama, TTS & System Control

A powerful, extensible AI assistant inspired by Iron Man's JARVIS. Features local LLM integration via Ollama, text-to-speech voice control, and comprehensive system automation capabilities.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **🧠 Local LLM Integration** - Powered by Ollama for private, offline AI
- **🗣️ Voice Control** - Wake word activation and speech recognition
- **🔊 Text-to-Speech** - Natural voice responses
- **⚙️ System Control** - Manage processes, files, and applications
- **🔍 Web Search** - Built-in search without external APIs
- **💾 Memory** - Persistent conversation and fact storage
- **🛠️ Extensible Skills** - Easy to add new capabilities
- **🎨 Rich UI** - Beautiful terminal interface

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.com/install.sh | sh

   # Or download from https://ollama.com/download
   ```

2. **Pull a Model**
   ```bash
   ollama pull llama3.2
   ```

### Installation

```bash
# Clone or create project directory
cd jarvis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### Usage

#### Interactive Chat Mode
```bash
python main.py
```

#### Voice-Controlled Mode
```bash
python main.py --voice
```

#### Single Command
```bash
python main.py --command "What's the weather in London?"
```

#### List Available Models
```bash
python main.py --list-models
```

## 🎙️ Voice Commands

When in voice mode, say:
- `"Jarvis"` - Wake word to activate
- `"What's the system info?"` - Get system information
- `"Open Chrome"` - Launch applications
- `"Search for Python tutorials"` - Web search
- `"What time is it?"` - Get current time
- `"List files in documents"` - File operations

## 🛠️ Available Tools

### System Control
- `system_info` - CPU, memory, disk usage
- `list_processes` - View running processes
- `kill_process` - Terminate processes
- `run_command` - Execute shell commands
- `open_app` - Launch applications
- `open_url` - Open websites

### File Operations
- `list_dir` - List directory contents
- `read_file` - Read file contents
- `write_file` - Write to files
- `search_files` - Find files by name

### Web & Information
- `web_search` - Search the web
- `weather` - Get weather information
- `time` - Current date and time

### Utilities
- `clipboard` - Copy to clipboard
- `calculate` - Mathematical calculations

## ⚙️ Configuration

Edit `.env` file:

```env
# Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Voice settings
VOICE_RATE=175
VOICE_VOLUME=1.0
WAKE_WORD=jarvis

# Paths
DOWNLOADS_PATH=~/Downloads
DOCUMENTS_PATH=~/Documents
```

## 🧩 Extending Jarvis

### Adding Custom Skills

```python
from jarvis.skills import Skill, SkillResult, skills

class MySkill(Skill):
    name = "my_skill"
    description = "Does something cool"
    triggers = ["do something"]

    def can_handle(self, command: str) -> bool:
        return any(t in command.lower() for t in self.triggers)

    def execute(self, command: str, **kwargs) -> SkillResult:
        # Your logic here
        return SkillResult(True, "Done!")

# Register the skill
skills.register(MySkill())
```

### Adding Tools

```python
from jarvis.tools import TOOLS

def my_tool(arg1: str) -> ToolResult:
    # Your logic
    return ToolResult(True, "Success", data={"key": "value"})

TOOLS["my_tool"] = my_tool
```

## 📁 Project Structure

```
jarvis/
├── jarvis/
│   ├── __init__.py
│   ├── agent.py          # Main orchestrator
│   ├── llm.py            # Ollama integration
│   ├── voice.py          # TTS & speech recognition
│   ├── tools.py          # System tools
│   ├── skills.py         # Extensible skills
│   ├── memory.py         # Vector memory
│   └── config.py         # Configuration
├── main.py               # Entry point
├── requirements.txt      # Dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## 🐛 Troubleshooting

### Voice not working
```bash
# Install audio dependencies
# Ubuntu/Debian:
sudo apt-get install portaudio19-dev python3-pyaudio

# macOS:
brew install portaudio
```

### Ollama connection issues
```bash
# Start Ollama server
ollama serve

# Verify connection
curl http://localhost:11434/api/tags
```

### Microphone issues
- Check microphone permissions
- Try `python -c "import speech_recognition as sr; r = sr.Recognizer(); print('OK')"`

## 📜 License

MIT License - Feel free to use and modify!

## 🙏 Acknowledgments

- [Ollama](https://ollama.com/) - Local LLM runtime
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- Inspired by Iron Man's JARVIS

---

> "Sometimes you gotta run before you can walk." - Tony Stark
