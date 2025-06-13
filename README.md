# Ziggy Voice Assistant

A sophisticated, local-first, privacy-focused voice assistant with GPU acceleration, conversational abilities, and modular architecture.

## ✨ Key Features

- **🔒 Local-First Privacy**: No web search or online functionality - purely local processing
- **🎤 Wake Word Detection**: "Ziggy" activation using Vosk speech recognition  
- **🧠 Dual AI Backend Support**: Works with both Msty and Ollama (auto-detects and can auto-start)
- **💬 Conversational Mode**: Natural multi-turn conversations without repeating wake word
- **⚡ Resource Profiles**: Adaptive performance based on available GPU memory
- **🎯 Smart Query Routing**: Local functions for simple tasks, GPU-accelerated AI for complex queries
- **🗣️ Voice Interruption**: Interrupt long responses by saying "Ziggy"
- **⚙️ Modular Architecture**: Clean, testable, maintainable codebase
- **🧪 Comprehensive Testing**: 72% test coverage with automated unit tests

## 🏗️ Architecture

This project features a clean, modular architecture that separates concerns and enables comprehensive testing:

### Original Monolithic Design
- Single 1665-line file with tightly coupled components
- Difficult to test and maintain
- Mixed responsibilities throughout

### New Modular Design
```
src/
├── audio/          # Audio I/O abstraction layer
├── speech/         # Speech recognition/synthesis with interruption
├── ai/             # AI backend management (Ollama/Msty) 
├── commands/       # Local command routing (time, date, math)
├── conversation/   # Conversation context management
├── resources/      # Resource profile management
└── utils/          # Utility functions

tests/              # Comprehensive test suite
├── test_audio.py   # Audio module tests
├── test_speech.py  # Speech module tests
├── test_ai_backend.py # AI backend tests
├── test_commands.py   # Command routing tests
├── test_conversation.py # Conversation tests
└── test_resources.py  # Resource management tests
```

## 🎯 Local-First Philosophy

Ziggy prioritizes privacy and local processing:
- **Local Functions**: Time, date, math, unit conversions handled without AI
- **No Online Access**: Web search functionality completely removed
- **Local AI Processing**: Uses your GPU for AI queries without sending data externally  
- **No Cloud Dependencies**: Everything runs on your hardware
- **Conversation History**: Stored in memory during session only

## 🛠️ System Requirements

### Hardware
- **CPU**: Multi-core processor
- **GPU**: 
  - **Minimum**: 4GB VRAM (integrated graphics or older GPUs)
  - **Recommended**: 8GB+ VRAM (NVIDIA or AMD GPU)
  - **Optimal**: 16GB+ VRAM for extended conversations
- **RAM**: 4GB+ system RAM
- **Audio**: Microphone and speakers/headphones

### Software
- **OS**: Linux (tested on Ubuntu 24.04.1 LTS)
- **Python**: 3.10+
- **AI Backend**: Msty or Ollama (assistant can auto-start if needed)

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/JoshGK8/voice_assist
cd voice_assist
```

### 2. Install System Dependencies

<details>
<summary>Scripted Install (Recommended)</summary>

```bash
# Run the system prerequisites installer
chmod +x system_prerequisites.sh
./system_prerequisites.sh
```

</details>

<details>
<summary>Manual Install</summary>

Install the following packages:
```bash
# Audio and speech libraries
sudo apt install portaudio19-dev espeak espeak-data libespeak1 libespeak-dev

# Build tools
sudo apt install build-essential python3-dev curl

# Optional: Audio troubleshooting tools
sudo apt install alsa-utils pulseaudio-utils

# Add user to audio group
sudo usermod -a -G audio $USER
```

</details>

**Important**: Log out and back in after installation to apply group changes.

### 3. Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv voice_assistant_env

# Activate environment
source voice_assistant_env/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install test dependencies (optional)
pip install -r requirements-test.txt
```

### 4. Download Speech Recognition Model
```bash
# Download Vosk model (~50MB)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

### 5. Set Up AI Backend (Optional)
The assistant will auto-detect running backends or offer to start one:

**Option A: Ollama** (Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (assistant will use first available)
ollama pull llama3.2
```

**Option B: Msty**
Download and install from [msty.app](https://msty.app)

### 6. Optional: Natural Voice Setup
For better voice quality than espeak:
```bash
chmod +x setup_piper.sh
./setup_piper.sh
```

## 🚀 Usage

### Available Versions

**Original Monolithic Version**:
```bash
source voice_assistant_env/bin/activate
python3 voice_assistant.py
```

**Clean Modular Version** (Recommended):
```bash
source voice_assistant_env/bin/activate
python3 voice_assistant_clean.py
```

Both versions have identical functionality, but the clean version uses the new modular architecture.

### Voice Commands

**Activation**: Say "Ziggy" to wake the assistant

**Conversational Mode**:
- Assistant automatically listens after asking questions
- No need to say "Ziggy" during conversations
- Maintains context across multiple exchanges
- Say "new conversation" to clear history

**Resource Profiles**:
- "Switch to gaming mode" - Minimal resource usage
- "Use standard profile" - Balanced performance  
- "Enable performance mode" - Maximum capabilities
- "What profile are you using?" - Check current status
- "How much memory?" - Get resource usage info

**Local Functions** (instant, no AI):
- "What time is it?"
- "What's the date?"
- "What's 25 plus 17?"
- "Convert 72 fahrenheit to celsius"
- "How many meters in 50 feet?"

**AI Queries** (uses local GPU):
- Complex questions and analysis
- Creative writing and coding help
- Technical explanations
- General knowledge (within training data)

**System Control**:
- "Take a break" - Shutdown assistant
- "Start over" / "New conversation" - Clear context
- "Ziggy" during long responses - Interrupt and start new command

### Conversational Flow Example
```
You: "Ziggy"
Ziggy: "Yes?"
You: "What's quantum computing?"
Ziggy: [Explains quantum computing and asks if you want to know more]
You: "Yes, how does it differ from regular computing?"  # No wake word needed!
Ziggy: [Continues explanation naturally]
```

## 🧪 Testing

The modular architecture enables comprehensive testing:

```bash
# Run all tests
./run_tests.sh

# Or use make targets
make test                # Run all tests
make test-coverage      # Run with coverage report
make test-unit          # Run only unit tests

# Run specific test modules
pytest tests/test_audio.py -v
pytest tests/test_commands.py -v
```

**Test Coverage**: 72% overall with comprehensive unit tests for all modules.

## ⚙️ Resource Profiles

Ziggy adapts to your system capabilities:

### Minimal Profile (Gaming/Multitasking)
- **Requirements**: 4-8GB VRAM
- **Context**: 8,000 tokens
- **History**: 10 conversation turns
- **Recording**: 2 minutes conversational, 30 seconds commands
- **Use Case**: Gaming while using assistant, older GPUs, shared systems

### Standard Profile (Daily Use)
- **Requirements**: 8-16GB VRAM
- **Context**: 16,000 tokens  
- **History**: 20 conversation turns
- **Recording**: 5 minutes conversational, 1 minute commands
- **Use Case**: General productivity, balanced performance

### Performance Profile (Research/Extended Use)
- **Requirements**: 16GB+ VRAM
- **Context**: 32,000 tokens
- **History**: 50 conversation turns
- **Recording**: 10 minutes conversational, 2 minutes commands
- **Use Case**: Long research sessions, complex discussions

**Profile Switching**: The assistant auto-detects your GPU memory and selects an appropriate profile. You can switch profiles with voice commands.

## 🔧 Configuration

### Customize Wake Word
Edit `voice_assistant_clean.py`:
```python
self.wake_word = "ziggy"  # Change to your preferred word
```

### Audio Settings
Adjust in the audio module configuration:
```python
sample_rate = 16000    # Audio sample rate
chunk_size = 1024      # Buffer size
```

## 🐛 Troubleshooting

### Audio Issues
```bash
# List devices
aplay -l    # Playback devices
arecord -l  # Recording devices

# Test microphone
arecord -d 5 test.wav && aplay test.wav

# Check permissions
groups | grep audio
```

### GPU Detection
```bash
# NVIDIA
nvidia-smi

# AMD  
rocm-smi --showmeminfo vram
# or
cat /sys/class/drm/card*/device/mem_info_vram_total
```

### AI Backend Issues
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check Msty
curl http://localhost:10002/v1/models

# The assistant will offer to start backends if not running
```

### Wake Word Problems
- Speak clearly and distinctly
- Reduce background noise
- Check microphone levels
- Consider environment acoustics

## 📊 Performance

### Resource Usage by Profile

| Profile | Idle RAM | Active RAM | GPU VRAM | Response Time |
|---------|----------|------------|----------|---------------|
| Minimal | ~100MB | ~200MB | 2-4GB | 1-3 seconds |
| Standard | ~150MB | ~300MB | 4-6GB | 1-5 seconds |
| Performance | ~200MB | ~400MB | 6-8GB | 2-8 seconds |

### Features by Profile

| Feature | Minimal | Standard | Performance |
|---------|---------|----------|-------------|
| Conversation Length | 10 turns | 20 turns | 50 turns |
| Context Window | 8K tokens | 16K tokens | 32K tokens |
| Recording Time | 2 min | 5 min | 10 min |
| Response Length | 500 tokens | 1000 tokens | 2000 tokens |

## 📁 Project Structure
```
voice_assist/
├── voice_assistant.py         # Original monolithic implementation
├── voice_assistant_clean.py   # Clean modular implementation  
├── src/                       # Modular source code
│   ├── audio/                 # Audio I/O abstraction
│   ├── speech/                # Speech processing & TTS
│   ├── ai/                    # AI backend management
│   ├── commands/              # Local command routing
│   ├── conversation/          # Context management
│   └── resources/             # Resource profiles
├── tests/                     # Comprehensive test suite
├── pytest.ini                # Test configuration
├── requirements.txt           # Python dependencies
├── requirements-test.txt      # Test dependencies
├── Makefile                   # Build targets
├── run_tests.sh              # Test runner script
├── setup_piper.sh            # Natural voice setup
└── system_prerequisites.sh   # System setup script
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch from main
3. Write tests for new functionality  
4. Ensure all tests pass: `make test`
5. Test all features work correctly
6. Ensure privacy principles are maintained
7. Submit pull request with clear description

## 📋 Recent Updates

### Version 2.0 - Modular Architecture (Current)
- ✅ **Complete modular refactoring** - Clean, testable architecture
- ✅ **Comprehensive testing** - 72% test coverage with unit tests
- ✅ **Removed web search** - Purely local processing
- ✅ **Enhanced interruption handling** - Interrupt responses with wake word
- ✅ **Improved conversation management** - Better context handling
- ✅ **Resource profile management** - Dynamic GPU memory detection
- ✅ **Command routing system** - Smart local vs AI query routing

### Version 1.0 - Original Implementation
- ✅ Dual backend support (Msty/Ollama)
- ✅ Conversational mode with automatic listening
- ✅ Resource profiles for different hardware
- ✅ Voice-controlled profile switching
- ✅ Improved natural language command recognition  
- ✅ Piper TTS integration option
- ✅ Auto backend startup with voice selection

## 📝 License

GPL-3.0 license

## 🙏 Acknowledgments

- **Vosk** for offline speech recognition
- **Ollama/Msty** for local AI backends
- **Piper TTS** for natural voice synthesis
- **espeak** for fallback text-to-speech
- **pytest** for comprehensive testing framework
- **Community** for testing and feedback

---

**Ziggy Voice Assistant** - Your local, private, AI-powered conversational companion with clean, maintainable code.