from abc import ABC, abstractmethod
from typing import Optional, Tuple
import numpy as np


class AudioInputInterface(ABC):
    """Interface for audio input operations"""
    
    @abstractmethod
    def start_stream(self) -> None:
        """Start the audio input stream"""
        pass
    
    @abstractmethod
    def stop_stream(self) -> None:
        """Stop the audio input stream"""
        pass
    
    @abstractmethod
    def read_chunk(self, num_frames: int) -> bytes:
        """Read audio chunk from the stream"""
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """Check if the stream is active"""
        pass


class AudioOutputInterface(ABC):
    """Interface for audio output operations"""
    
    @abstractmethod
    def play_audio(self, audio_data: bytes, sample_rate: int = 22050) -> None:
        """Play audio data"""
        pass
    
    @abstractmethod
    def stop_playback(self) -> None:
        """Stop current audio playback"""
        pass
    
    @abstractmethod
    def is_playing(self) -> bool:
        """Check if audio is currently playing"""
        pass


class AudioRecorderInterface(ABC):
    """Interface for audio recording operations"""
    
    @abstractmethod
    def record(self, duration: float, sample_rate: int = 16000) -> Tuple[np.ndarray, int]:
        """Record audio for specified duration"""
        pass
    
    @abstractmethod
    def record_until_silence(self, max_duration: float = 10.0, 
                           silence_threshold: float = 0.01,
                           silence_duration: float = 1.0) -> Tuple[np.ndarray, int]:
        """Record until silence is detected"""
        pass