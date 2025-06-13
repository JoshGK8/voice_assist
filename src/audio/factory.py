from typing import Optional
from .interfaces import AudioInputInterface, AudioOutputInterface, AudioRecorderInterface
from .pyaudio_impl import PyAudioInput, PyAudioOutput, PyAudioRecorder


class AudioFactory:
    """Factory for creating audio components"""
    
    @staticmethod
    def create_input(backend: str = "pyaudio", 
                    device_index: Optional[int] = None,
                    **kwargs) -> AudioInputInterface:
        """Create audio input instance"""
        if backend == "pyaudio":
            return PyAudioInput(device_index=device_index, **kwargs)
        else:
            raise ValueError(f"Unknown audio backend: {backend}")
    
    @staticmethod
    def create_output(backend: str = "pyaudio",
                     device_index: Optional[int] = None,
                     **kwargs) -> AudioOutputInterface:
        """Create audio output instance"""
        if backend == "pyaudio":
            return PyAudioOutput(device_index=device_index, **kwargs)
        else:
            raise ValueError(f"Unknown audio backend: {backend}")
    
    @staticmethod
    def create_recorder(backend: str = "pyaudio",
                       device_index: Optional[int] = None,
                       **kwargs) -> AudioRecorderInterface:
        """Create audio recorder instance"""
        if backend == "pyaudio":
            return PyAudioRecorder(device_index=device_index, **kwargs)
        else:
            raise ValueError(f"Unknown audio backend: {backend}")