from typing import Optional
from .interfaces import (
    SpeechRecognitionInterface,
    TextToSpeechInterface,
    WakeWordDetectorInterface
)
from .vosk_impl import VoskSpeechRecognition, VoskWakeWordDetector
from .tts_impl import EspeakTTS, PiperTTS


class SpeechFactory:
    """Factory for creating speech components"""
    
    @staticmethod
    def create_recognizer(backend: str = "vosk",
                         model_path: Optional[str] = None,
                         **kwargs) -> SpeechRecognitionInterface:
        """Create speech recognition instance"""
        if backend == "vosk":
            if not model_path:
                raise ValueError("model_path required for Vosk")
            return VoskSpeechRecognition(model_path, **kwargs)
        else:
            raise ValueError(f"Unknown speech recognition backend: {backend}")
    
    @staticmethod
    def create_tts(backend: str = "espeak",
                  **kwargs) -> TextToSpeechInterface:
        """Create text-to-speech instance"""
        if backend == "espeak":
            return EspeakTTS(**kwargs)
        elif backend == "piper":
            return PiperTTS(**kwargs)
        else:
            raise ValueError(f"Unknown TTS backend: {backend}")
    
    @staticmethod
    def create_wake_word_detector(backend: str = "vosk",
                                 model_path: Optional[str] = None,
                                 wake_word: str = "ziggy",
                                 **kwargs) -> WakeWordDetectorInterface:
        """Create wake word detector instance"""
        if backend == "vosk":
            if not model_path:
                raise ValueError("model_path required for Vosk")
            return VoskWakeWordDetector(model_path, wake_word, **kwargs)
        else:
            raise ValueError(f"Unknown wake word backend: {backend}")