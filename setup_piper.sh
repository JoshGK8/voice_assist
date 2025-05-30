#!/bin/bash

# Setup script for Piper TTS (natural voice)
# This provides a much more pleasant voice than espeak

echo "Setting up Piper TTS for natural voice..."

# Create directory
mkdir -p ~/.local/share/piper
cd ~/.local/share/piper

# Download Piper binary
if [ ! -f "piper/piper" ]; then
    echo "Downloading Piper binary..."
    wget -q https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
    tar -xzf piper_amd64.tar.gz
    rm piper_amd64.tar.gz
    echo "✓ Piper binary installed"
else
    echo "✓ Piper binary already installed"
fi

# Download Amy voice model (pleasant female voice)
if [ ! -f "en_US-amy-medium.onnx" ]; then
    echo "Downloading Amy voice model..."
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json
    echo "✓ Voice model installed"
else
    echo "✓ Voice model already installed"
fi

# Test Piper
echo "Testing Piper..."
echo "Hello! This is your new natural voice assistant." | ./piper/piper --model en_US-amy-medium.onnx --output_file test.wav
if [ -f "test.wav" ]; then
    aplay test.wav 2>/dev/null
    rm test.wav
    echo "✓ Piper is working!"
    echo ""
    echo "Piper has been set up successfully!"
    echo "The voice assistant will automatically use this natural voice."
else
    echo "⚠ Piper test failed. The assistant will fall back to espeak."
fi

echo ""
echo "Alternative voices you can try:"
echo "- en_US-lessac-medium: Professional male voice"
echo "- en_US-libritts_r-medium: Clear female voice"
echo "- en_GB-jenny_dioco-medium: British female voice"
echo ""
echo "To change voices, download a different model and update voice_assistant.py"