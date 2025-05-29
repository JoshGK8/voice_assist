#!/bin/bash
# Voice Assistant System Prerequisites
# Ubuntu 24.04.1 LTS Package Installation Script
# Run with: bash system-prerequisites.txt

echo "Installing Voice Assistant System Prerequisites..."

# Update package list
sudo apt update

# Audio system dependencies (required)
sudo apt install -y portaudio19-dev
sudo apt install -y espeak espeak-data libespeak1 libespeak-dev

# Build tools (required for Python package compilation)
sudo apt install -y build-essential python3-dev

# Network tools (for testing connections)
sudo apt install -y curl

# Audio troubleshooting tools (optional but recommended)
sudo apt install -y alsa-utils pulseaudio-utils

# Add current user to audio group (IMPORTANT)
echo "Adding $USER to audio group..."
sudo usermod -a -G audio $USER

echo ""
echo "✅ System prerequisites installed successfully!"
echo ""
echo "IMPORTANT: You must logout and login again for audio permissions to take effect."
echo ""
echo "After logout/login, run these commands:"
echo "1. pip install -r requirements.txt"
echo "2. wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
echo "3. unzip vosk-model-small-en-us-0.15.zip"
echo "4. Start msty.app on localhost:10000"
echo "5. Begin testing with: python3 test_audio_system.py"