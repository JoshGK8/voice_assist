from abc import ABC, abstractmethod
from typing import Optional, List, Union, Callable
import numpy as np


class SpeechRecognitionInterface(ABC):
    """Interface for speech recognition operations"""
    
    @abstractmethod
    def recognize(self, audio_data: Union[bytes, np.ndarray], 
                 sample_rate: int = 16000) -> Optional[str]:
        """Convert speech to text"""
        pass
    
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if the recognizer is ready"""
        pass


class TextToSpeechInterface(ABC):
    """Interface for text-to-speech operations"""
    
    @abstractmethod
    def speak(self, text: str) -> None:
        """Convert text to speech and play it"""
        pass
    
    @abstractmethod
    def speak_async(self, text: str) -> None:
        """Convert text to speech asynchronously"""
        pass
    
    @abstractmethod
    def stop_speaking(self) -> None:
        """Stop current speech"""
        pass
    
    @abstractmethod
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        pass
    
    @abstractmethod
    def get_audio_data(self, text: str) -> bytes:
        """Get audio data without playing"""
        pass
    
    @abstractmethod
    def speak_with_interruption(self, text: str, 
                               interruption_detector: Optional[Callable[[], bool]] = None) -> bool:
        """Speak text with interruption capability. Returns True if interrupted."""
        pass


class WakeWordDetectorInterface(ABC):
    """Interface for wake word detection"""
    
    @abstractmethod
    def detect(self, audio_data: Union[bytes, np.ndarray],
              sample_rate: int = 16000) -> bool:
        """Detect if wake word is present in audio"""
        pass
    
    @abstractmethod
    def get_wake_word(self) -> str:
        """Get the configured wake word"""
        pass
    
    @abstractmethod
    def set_wake_word(self, wake_word: str) -> None:
        """Set a new wake word"""
        pass