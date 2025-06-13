#!/usr/bin/env python3
"""
Refactored Voice Assistant using modular architecture
"""
import os
import time
from pathlib import Path

from src.audio import AudioFactory
from src.speech import SpeechFactory
from src.ai import AIBackendManager


class RefactoredVoiceAssistant:
    """Voice assistant using new modular architecture"""
    
    def __init__(self):
        # Initialize components using factories
        self.audio_input = AudioFactory.create_input("pyaudio")
        self.audio_recorder = AudioFactory.create_recorder("pyaudio")
        
        # Initialize speech components
        model_path = "vosk-model-small-en-us-0.15"
        self.speech_recognizer = SpeechFactory.create_recognizer(
            "vosk", 
            model_path=model_path
        )
        self.wake_word_detector = SpeechFactory.create_wake_word_detector(
            "vosk",
            model_path=model_path,
            wake_word="ziggy"
        )
        self.tts = SpeechFactory.create_tts("espeak", voice="en", speed=150)
        
        # Initialize AI backend
        self.ai_manager = AIBackendManager()
        
    def setup(self):
        """Setup the voice assistant"""
        print("🚀 Initializing Refactored Voice Assistant...")
        
        # Setup AI backend
        backend_type = self.ai_manager.detect_backend()
        if not backend_type:
            print("❌ No AI backend detected. Please start Ollama or Msty.")
            return False
            
        print(f"✅ Connected to {backend_type} backend")
        return True
    
    def listen_for_wake_word(self):
        """Listen for wake word"""
        print("👂 Listening for 'ziggy'...")
        
        while True:
            try:
                # Record audio
                audio_data, sample_rate = self.audio_recorder.record(duration=2.0)
                
                # Check for wake word
                if self.wake_word_detector.detect(audio_data, sample_rate):
                    print("👋 Wake word detected!")
                    return True
                    
            except KeyboardInterrupt:
                return False
    
    def process_command(self):
        """Process voice command"""
        print("🎤 Listening for command...")
        
        # Record command
        audio_data, sample_rate = self.audio_recorder.record_until_silence(
            max_duration=10.0,
            silence_threshold=0.01,
            silence_duration=1.0
        )
        
        # Convert to text
        command_text = self.speech_recognizer.recognize(audio_data, sample_rate)
        if not command_text:
            print("❌ Could not understand command")
            return
            
        print(f"📝 Command: {command_text}")
        
        # Process with AI
        backend = self.ai_manager.get_backend()
        if backend:
            response = backend.query(command_text)
            if response.error:
                print(f"❌ AI Error: {response.error}")
            else:
                print(f"🤖 Response: {response.content}")
                self.tts.speak(response.content)
        else:
            print("❌ No AI backend available")
    
    def run(self):
        """Main run loop"""
        if not self.setup():
            return
            
        print("🎯 Voice assistant ready! Say 'ziggy' to start.")
        
        try:
            while True:
                if self.listen_for_wake_word():
                    self.process_command()
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")


def main():
    """Main entry point"""
    assistant = RefactoredVoiceAssistant()
    assistant.run()


if __name__ == "__main__":
    main()