# Ziggy Voice Assistant

A local-first, privacy-focused voice assistant with GPU acceleration and smart query routing.

## ✨ Features

- **🔒 Local-First Privacy**: Explicit permission required for any online activity
- **🎤 Custom Wake Word**: "Ziggy" detection using Vosk speech recognition
- **🧠 Smart Query Routing**: Local functions for simple tasks, GPU-accelerated AI for complex queries
- **🗣️ Natural Voice Responses**: Text-to-speech output with espeak
- **⚡ GPU Acceleration**: ROCm-powered AI responses via local msty.app/Ollama
- **🚀 Auto-Start Ready**: Boot-time activation with welcome message
- **⏹️ Voice Shutdown**: "Ziggy, take a break" for graceful shutdown

## 🎯 Local-First Philosophy

Ziggy prioritizes privacy and local processing:
- **Local Functions**: Time, date, unit conversions handled without AI
- **Permission-Gated Online Access**: Explicit consent required for web searches
- **Local AI Processing**: Uses your GPU for AI queries without sending data externally
- **No Cloud Dependencies**: Everything runs on your hardware

## 🛠️ System Requirements

### Hardware
- **CPU**: Multi-core processor (tested on AMD Ryzen 9 5950X)
- **GPU**: AMD GPU with ROCm support (tested on RX 7900 XTX)
- **RAM**: 4GB+ (8GB+ recommended for larger AI models)
- **Audio**: Microphone and speakers/headphones

### Software
- **OS**: Ubuntu 24.04.1 LTS (or compatible Debian-based system)
- **Python**: 3.12+
- **AI Backend**: msty.app or Ollama running locally on port 10000

## 📦 Installation

### 1. Clone Directory
```bash
git clone https://github.com/JoshGK8/voice_assist
cd voice_assist
```

### 2. Install System Dependencies

You can install the system dependencies either via a shell script or manually. 
<details>
  
<summary>Scripted Install</summary>

 
I have provided the same shell script I use to configure my machine (running Ubuntu 24.04):

```bash
# Run the system prerequisites installer
chmod +x system_prerequisites.sh
./system_prerequisites.sh
```

</details>

<details>
  
<summary>Manual Install</summary>

 
Manually install the following:

- ``portaudio19-dev``
- ``espeak espeak-data libespeak1 libespeak-dev``
- ``build-essential python3-dev``
- ``curl``

Optionally, these tools can help with troubleshooting audio issues:

- ``alsa-utils pulseaudio-utils``

Add your user to the *audio* group:

```bash
echo "Adding $USER to audio group..."
sudo usermod -a -G audio $USER
```

</details>

After installing the prerequisites, log out and back in to complete the group membership update.

### 3. Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv voice_assistant_env

# Activate environment
source voice_assistant_env/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Download Speech Recognition Model
```bash
# Download Vosk model (~50MB)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

### 5. Configure AI Backend
Ensure msty.app/Ollama is running locally:
```bash
# Verify AI backend is accessible
curl http://localhost:10000/v1/models
```

## 🚀 Usage

### Start the Voice Assistant
```bash
# Activate virtual environment
source voice_assistant_env/bin/activate

# Run Ziggy
python3 voice_assistant.py
```

### Voice Commands

**Activation**: Say "Ziggy" to wake the assistant

**Local Functions** (no AI needed):
- "What time is it?"
- "What's today's date?"
- "Convert 32 fahrenheit to celsius"

**AI Queries** (uses local GPU):
- "Explain quantum computing"
- "Write a haiku about computers"
- "How do I fix a GPU driver issue?"

**Web Search** (requires permission):
- "Search for weather forecast"
- "Look up Ubuntu release notes"

**Shutdown**: Say "Ziggy, take a break"

### Privacy Protection

When Ziggy needs online resources, it will ask:
> "I cannot answer that from my local resources. Do you want me to check online?"

Respond with "yes" to grant permission, or "no" to stay local.

## ⚙️ Configuration

### Wake Word Customization
Edit `voice_assistant.py` to change wake word:
```python
self.wake_word = "ziggy"  # Change to your preferred word
```

### AI Model Selection
The assistant automatically uses the first available model from your AI backend. To specify a model:
```python
self.default_model = "llama3.2:latest"  # Set specific model
```

### Audio Settings
Adjust audio parameters in `voice_assistant.py`:
```python
self.sample_rate = 16000    # Audio sample rate
self.chunk_size = 4000      # Buffer size
```

## 🔧 Auto-Start Setup

### systemd Service (Run at Boot)
```bash
# Create service file
sudo tee /etc/systemd/system/ziggy.service << 'EOF'
[Unit]
Description=Ziggy Voice Assistant
After=graphical.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/voice_assist
ExecStart=/path/to/voice_assist/voice_assistant_env/bin/python /path/to/voice_assist/voice_assistant.py
Restart=always
RestartSec=5
Environment=DISPLAY=:0

[Install]
WantedBy=graphical.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ziggy.service
sudo systemctl start ziggy.service
```

### Desktop Autostart (User Session)
```bash
# Create autostart entry
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/ziggy.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Ziggy Voice Assistant
Exec=/path/to/voice_assist/voice_assistant_env/bin/python /path/to/voice_assist/voice_assistant.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

## 🐛 Troubleshooting

### Audio Issues
```bash
# Check audio devices
aplay -l    # List playback devices
arecord -l  # List recording devices

# Verify user is in audio group
groups | grep audio

# Fix audio permissions
sudo usermod -a -G audio $USER
# Then logout and login
```

### Speech Recognition Problems
- Ensure Vosk model is downloaded and extracted
- Check microphone is working: `python3 test_audio_system.py`
- Reduce background noise
- Speak clearly and at normal volume

### AI Backend Connection
```bash
# Check if msty.app/Ollama is running
curl http://localhost:10000/v1/models

# Verify GPU acceleration
amdgpu_top  # Should show activity during AI queries
```

### Wake Word Detection
- Speak "Ziggy" clearly and distinctly
- Try adjusting microphone volume/positioning
- Consider training custom wake word for better accuracy

## 🎨 Voice Quality Upgrades

### Replace espeak with Piper TTS
For higher quality voice synthesis:
```bash
pip install piper-tts
# Download Piper voice models and modify voice_assistant.py
```

### Better Wake Word Detection
For improved accuracy, consider training custom models with your voice.

## 🔄 Development

### Project Structure
```
voice_assist/
├── voice_assistant.py     # Main integrated assistant
├── test_*.py             # Individual component tests
├── requirements.txt      # Python dependencies
├── system-prerequisites.sh # System setup
└── README.md            # This file
```

### Adding New Local Functions
Add functions to the `VoiceAssistant` class and update `route_query()` method to recognize new command patterns.

### Extending AI Capabilities
Modify system prompts in `query_ai_local_only()` to customize AI behavior.

## 📊 Performance

### Resource Usage
- **Idle**: ~50MB RAM, minimal CPU
- **Active Listening**: ~100MB RAM, <5% CPU  
- **AI Processing**: Brief GPU utilization, <2GB VRAM

### Response Times
- **Local Functions**: <100ms
- **AI Queries**: 1-5 seconds (depending on model and query complexity)
- **Wake Word Detection**: Real-time (<50ms latency)

## 🤝 Contributing

1. Fork the repository
2. Test all components with `test_*.py` scripts
3. Ensure privacy principles are maintained
4. Submit pull request with clear description

## 📋 Todo / Future Improvements

- [ ] Piper TTS integration for better voice quality
- [ ] Custom wake word training pipeline
- [ ] Plugin system for extensible functionality
- [ ] Web interface for configuration
- [ ] Support for multiple AI backends
- [ ] Voice command history and learning
- [ ] Integration with home automation systems

## 📝 License

GPL-3.0 license

## 🙏 Acknowledgments

- **Vosk** for offline speech recognition
- **Porcupine/Custom wake word** for activation detection
- **msty.app/Ollama** for local AI backend
- **espeak** for text-to-speech synthesis
- **AMD ROCm** for GPU acceleration

---

**Ziggy Voice Assistant** - Your local, private, AI-powered voice companion.
