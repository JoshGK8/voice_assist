import pyaudio
import numpy as np
import time
import threading
from typing import Optional, Tuple
from .interfaces import AudioInputInterface, AudioOutputInterface, AudioRecorderInterface


class PyAudioInput(AudioInputInterface):
    """PyAudio implementation of audio input"""
    
    def __init__(self, device_index: Optional[int] = None, 
                 channels: int = 1, 
                 sample_rate: int = 16000,
                 chunk_size: int = 1024):
        self.device_index = device_index
        self.channels = channels
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
    def start_stream(self) -> None:
        """Start the audio input stream"""
        if self.stream is None or not self.stream.is_active():
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size
            )
    
    def stop_stream(self) -> None:
        """Stop the audio input stream"""
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def read_chunk(self, num_frames: int) -> bytes:
        """Read audio chunk from the stream"""
        if not self.stream or not self.stream.is_active():
            raise RuntimeError("Audio stream is not active")
        return self.stream.read(num_frames, exception_on_overflow=False)
    
    def is_active(self) -> bool:
        """Check if the stream is active"""
        return self.stream is not None and self.stream.is_active()
    
    def __del__(self):
        """Cleanup resources"""
        self.stop_stream()
        self.audio.terminate()


class PyAudioOutput(AudioOutputInterface):
    """PyAudio implementation of audio output"""
    
    def __init__(self, device_index: Optional[int] = None,
                 channels: int = 1):
        self.device_index = device_index
        self.channels = channels
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_playing_flag = False
        self.playback_thread = None
        self._stop_playback = threading.Event()
        
    def play_audio(self, audio_data: bytes, sample_rate: int = 22050) -> None:
        """Play audio data"""
        self.stop_playback()
        self._stop_playback.clear()
        self.playback_thread = threading.Thread(
            target=self._playback_worker,
            args=(audio_data, sample_rate)
        )
        self.playback_thread.start()
    
    def _playback_worker(self, audio_data: bytes, sample_rate: int) -> None:
        """Worker thread for audio playback"""
        self.is_playing_flag = True
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=sample_rate,
                output=True,
                output_device_index=self.device_index
            )
            
            # Play audio in chunks
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size):
                if self._stop_playback.is_set():
                    break
                chunk = audio_data[i:i + chunk_size]
                self.stream.write(chunk)
                
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            self.is_playing_flag = False
    
    def stop_playback(self) -> None:
        """Stop current audio playback"""
        self._stop_playback.set()
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=1.0)
        self.is_playing_flag = False
    
    def is_playing(self) -> bool:
        """Check if audio is currently playing"""
        return self.is_playing_flag
    
    def __del__(self):
        """Cleanup resources"""
        self.stop_playback()
        self.audio.terminate()


class PyAudioRecorder(AudioRecorderInterface):
    """PyAudio implementation of audio recording"""
    
    def __init__(self, device_index: Optional[int] = None,
                 channels: int = 1):
        self.device_index = device_index
        self.channels = channels
        self.audio = pyaudio.PyAudio()
        
    def record(self, duration: float, sample_rate: int = 16000) -> Tuple[np.ndarray, int]:
        """Record audio for specified duration"""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=1024
        )
        
        frames = []
        chunk_size = 1024
        num_chunks = int(sample_rate * duration / chunk_size)
        
        for _ in range(num_chunks):
            data = stream.read(chunk_size)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        # Convert to numpy array
        audio_data = b''.join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        return audio_array, sample_rate
    
    def record_until_silence(self, max_duration: float = 10.0, 
                           silence_threshold: float = 0.01,
                           silence_duration: float = 1.0) -> Tuple[np.ndarray, int]:
        """Record until silence is detected"""
        sample_rate = 16000
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=1024
        )
        
        frames = []
        chunk_size = 1024
        silence_chunks = int(silence_duration * sample_rate / chunk_size)
        consecutive_silence = 0
        max_chunks = int(max_duration * sample_rate / chunk_size)
        
        for i in range(max_chunks):
            data = stream.read(chunk_size)
            frames.append(data)
            
            # Check for silence
            audio_chunk = np.frombuffer(data, dtype=np.int16)
            volume = np.abs(audio_chunk).mean() / 32768.0
            
            if volume < silence_threshold:
                consecutive_silence += 1
                if consecutive_silence >= silence_chunks:
                    break
            else:
                consecutive_silence = 0
        
        stream.stop_stream()
        stream.close()
        
        # Convert to numpy array
        audio_data = b''.join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        return audio_array, sample_rate
    
    def __del__(self):
        """Cleanup resources"""
        self.audio.terminate()