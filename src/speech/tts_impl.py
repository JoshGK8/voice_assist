import subprocess
import threading
import tempfile
import os
import queue
import re
import time
from typing import Optional, List, Callable
from .interfaces import TextToSpeechInterface


class EspeakTTS(TextToSpeechInterface):
    """Espeak implementation of text-to-speech"""
    
    def __init__(self, voice: str = "en", speed: int = 150):
        self.voice = voice
        self.speed = speed
        self.current_process = None
        self.is_speaking_flag = False
        self.speaking_lock = threading.Lock()
    
    def speak(self, text: str) -> None:
        """Convert text to speech and play it"""
        with self.speaking_lock:
            self.stop_speaking()
            self.is_speaking_flag = True
            
        try:
            self.current_process = subprocess.Popen([
                'espeak',
                '-s', str(self.speed),
                '-v', self.voice,
                text
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.current_process.wait()
            
        finally:
            with self.speaking_lock:
                self.is_speaking_flag = False
                self.current_process = None
    
    def speak_async(self, text: str) -> None:
        """Convert text to speech asynchronously"""
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()
    
    def stop_speaking(self) -> None:
        """Stop current speech"""
        with self.speaking_lock:
            if self.current_process:
                self.current_process.terminate()
                self.current_process = None
            self.is_speaking_flag = False
    
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        return self.is_speaking_flag
    
    def get_audio_data(self, text: str) -> bytes:
        """Get audio data without playing"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            subprocess.run([
                'espeak',
                '-s', str(self.speed),
                '-v', self.voice,
                '-w', tmp_path,
                text
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            with open(tmp_path, 'rb') as f:
                return f.read()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def speak_with_interruption(self, text: str, 
                               interruption_detector: Optional[Callable[[], bool]] = None) -> bool:
        """Speak text with interruption capability"""
        from .interruption import InterruptibleTTS
        
        # Create interruptible wrapper
        interruptible = InterruptibleTTS(self)
        return interruptible.speak_with_interruption(text, interruption_detector)


class PiperTTS(TextToSpeechInterface):
    """Piper implementation of text-to-speech"""
    
    def __init__(self, piper_path: str, model_path: str, sample_rate: int = 22050):
        self.piper_path = piper_path
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.current_process = None
        self.is_speaking_flag = False
        self.speaking_lock = threading.Lock()
        
        # Check if piper is available
        self.available = os.path.exists(piper_path) and os.path.exists(model_path)
    
    def speak(self, text: str) -> None:
        """Convert text to speech and play it"""
        if not self.available:
            raise RuntimeError("Piper TTS not available")
        
        with self.speaking_lock:
            self.stop_speaking()
            self.is_speaking_flag = True
        
        try:
            # Escape single quotes in text
            escaped_text = text.replace("'", "'\"'\"'")
            
            # Generate audio with Piper
            piper_process = subprocess.Popen(
                f"echo '{escaped_text}' | {self.piper_path} --model {self.model_path} --output-raw",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            
            # Play the audio
            self.current_process = subprocess.Popen(
                ['aplay', '-r', str(self.sample_rate), '-f', 'S16_LE', '-t', 'raw', '-'],
                stdin=piper_process.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.current_process.wait()
            
        finally:
            with self.speaking_lock:
                self.is_speaking_flag = False
                self.current_process = None
    
    def speak_async(self, text: str) -> None:
        """Convert text to speech asynchronously"""
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()
    
    def stop_speaking(self) -> None:
        """Stop current speech"""
        with self.speaking_lock:
            if self.current_process:
                self.current_process.terminate()
                self.current_process = None
            self.is_speaking_flag = False
    
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        return self.is_speaking_flag
    
    def get_audio_data(self, text: str) -> bytes:
        """Get audio data without playing"""
        if not self.available:
            raise RuntimeError("Piper TTS not available")
        
        escaped_text = text.replace("'", "'\"'\"'")
        
        process = subprocess.Popen(
            f"echo '{escaped_text}' | {self.piper_path} --model {self.model_path} --output-raw",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        
        audio_data, _ = process.communicate()
        return audio_data
    
    def speak_with_interruption(self, text: str, 
                               interruption_detector: Optional[Callable[[], bool]] = None) -> bool:
        """Speak text with interruption capability"""
        from .interruption import InterruptibleTTS
        
        # Create interruptible wrapper
        interruptible = InterruptibleTTS(self)
        return interruptible.speak_with_interruption(text, interruption_detector)