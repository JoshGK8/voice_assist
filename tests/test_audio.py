"""
Unit tests for audio module
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from audio.interfaces import AudioInputInterface, AudioOutputInterface, AudioRecorderInterface
from audio.factory import AudioFactory


class TestAudioInterfaces:
    """Test audio interfaces"""
    
    def test_audio_input_interface(self):
        """Test AudioInputInterface is abstract"""
        with pytest.raises(TypeError):
            AudioInputInterface()
    
    def test_audio_output_interface(self):
        """Test AudioOutputInterface is abstract"""
        with pytest.raises(TypeError):
            AudioOutputInterface()
    
    def test_audio_recorder_interface(self):
        """Test AudioRecorderInterface is abstract"""
        with pytest.raises(TypeError):
            AudioRecorderInterface()


class TestAudioFactory:
    """Test AudioFactory"""
    
    @patch('audio.pyaudio_impl.pyaudio.PyAudio')
    def test_create_input(self, mock_pyaudio):
        """Test creating audio input"""
        mock_pyaudio.return_value = MagicMock()
        
        audio_input = AudioFactory.create_input(backend="pyaudio")
        assert audio_input is not None
        assert hasattr(audio_input, 'start_stream')
        assert hasattr(audio_input, 'stop_stream')
        assert hasattr(audio_input, 'read_chunk')
        assert hasattr(audio_input, 'is_active')
    
    @patch('audio.pyaudio_impl.pyaudio.PyAudio')
    def test_create_output(self, mock_pyaudio):
        """Test creating audio output"""
        mock_pyaudio.return_value = MagicMock()
        
        audio_output = AudioFactory.create_output(backend="pyaudio")
        assert audio_output is not None
        assert hasattr(audio_output, 'play_audio')
        assert hasattr(audio_output, 'stop_playback')
        assert hasattr(audio_output, 'is_playing')
    
    @patch('audio.pyaudio_impl.pyaudio.PyAudio')
    def test_create_recorder(self, mock_pyaudio):
        """Test creating audio recorder"""
        mock_pyaudio.return_value = MagicMock()
        
        recorder = AudioFactory.create_recorder(backend="pyaudio")
        assert recorder is not None
        assert hasattr(recorder, 'record')
        assert hasattr(recorder, 'record_until_silence')
    
    def test_unknown_backend(self):
        """Test error on unknown backend"""
        with pytest.raises(ValueError, match="Unknown audio backend"):
            AudioFactory.create_input(backend="unknown")


class TestPyAudioInput:
    """Test PyAudioInput implementation"""
    
    @patch('audio.pyaudio_impl.pyaudio.PyAudio')
    def test_start_stop_stream(self, mock_pyaudio):
        """Test starting and stopping stream"""
        from audio.pyaudio_impl import PyAudioInput
        
        mock_audio = MagicMock()
        mock_stream = MagicMock()
        mock_audio.open.return_value = mock_stream
        mock_pyaudio.return_value = mock_audio
        
        audio_input = PyAudioInput()
        
        # Test start
        audio_input.start_stream()
        mock_audio.open.assert_called_once()
        assert audio_input.stream == mock_stream
        
        # Test is_active
        mock_stream.is_active.return_value = True
        assert audio_input.is_active() is True
        
        # Test stop
        audio_input.stop_stream()
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
        assert audio_input.stream is None
    
    @patch('audio.pyaudio_impl.pyaudio.PyAudio')
    def test_read_chunk(self, mock_pyaudio):
        """Test reading audio chunk"""
        from audio.pyaudio_impl import PyAudioInput
        
        mock_audio = MagicMock()
        mock_stream = MagicMock()
        mock_stream.is_active.return_value = True
        mock_stream.read.return_value = b'test_audio_data'
        mock_audio.open.return_value = mock_stream
        mock_pyaudio.return_value = mock_audio
        
        audio_input = PyAudioInput()
        audio_input.start_stream()
        
        data = audio_input.read_chunk(1024)
        assert data == b'test_audio_data'
        mock_stream.read.assert_called_with(1024, exception_on_overflow=False)
    
    @patch('audio.pyaudio_impl.pyaudio.PyAudio')
    def test_read_chunk_no_stream(self, mock_pyaudio):
        """Test reading chunk without active stream"""
        from audio.pyaudio_impl import PyAudioInput
        
        mock_pyaudio.return_value = MagicMock()
        audio_input = PyAudioInput()
        
        with pytest.raises(RuntimeError, match="Audio stream is not active"):
            audio_input.read_chunk(1024)


class TestPyAudioOutput:
    """Test PyAudioOutput implementation"""
    
    @patch('audio.pyaudio_impl.pyaudio.PyAudio')
    @patch('audio.pyaudio_impl.threading.Thread')
    def test_play_audio(self, mock_thread, mock_pyaudio):
        """Test playing audio"""
        from audio.pyaudio_impl import PyAudioOutput
        
        mock_audio = MagicMock()
        mock_pyaudio.return_value = mock_audio
        
        audio_output = PyAudioOutput()
        audio_data = b'test_audio'
        
        # Test play_audio
        audio_output.play_audio(audio_data, sample_rate=22050)
        
        # Verify thread was started
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    @patch('audio.pyaudio_impl.pyaudio.PyAudio')
    def test_stop_playback(self, mock_pyaudio):
        """Test stopping playback"""
        from audio.pyaudio_impl import PyAudioOutput
        
        mock_pyaudio.return_value = MagicMock()
        audio_output = PyAudioOutput()
        
        # Set up mock thread
        mock_thread = MagicMock()
        mock_thread.is_alive.return_value = True
        audio_output.playback_thread = mock_thread
        audio_output.is_playing_flag = True
        
        # Test stop
        audio_output.stop_playback()
        
        assert audio_output._stop_playback.is_set()
        mock_thread.join.assert_called_with(timeout=1.0)
        assert audio_output.is_playing_flag is False


class TestPyAudioRecorder:
    """Test PyAudioRecorder implementation"""
    
    @patch('audio.pyaudio_impl.pyaudio.PyAudio')
    def test_record(self, mock_pyaudio):
        """Test recording audio"""
        from audio.pyaudio_impl import PyAudioRecorder
        
        mock_audio = MagicMock()
        mock_stream = MagicMock()
        
        # Mock audio data
        mock_data = np.zeros(1024, dtype=np.int16).tobytes()
        mock_stream.read.return_value = mock_data
        mock_audio.open.return_value = mock_stream
        mock_pyaudio.return_value = mock_audio
        
        recorder = PyAudioRecorder()
        audio_array, sample_rate = recorder.record(duration=0.1, sample_rate=16000)
        
        assert isinstance(audio_array, np.ndarray)
        assert sample_rate == 16000
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
    
    @patch('audio.pyaudio_impl.pyaudio.PyAudio')
    def test_record_until_silence(self, mock_pyaudio):
        """Test recording until silence"""
        from audio.pyaudio_impl import PyAudioRecorder
        
        mock_audio = MagicMock()
        mock_stream = MagicMock()
        
        # Mock audio data - first loud, then silence
        loud_data = np.full(1024, 1000, dtype=np.int16).tobytes()
        silent_data = np.zeros(1024, dtype=np.int16).tobytes()
        
        mock_stream.read.side_effect = [loud_data, loud_data, silent_data, silent_data]
        mock_audio.open.return_value = mock_stream
        mock_pyaudio.return_value = mock_audio
        
        recorder = PyAudioRecorder()
        audio_array, sample_rate = recorder.record_until_silence(
            max_duration=1.0,
            silence_threshold=0.01,
            silence_duration=0.1
        )
        
        assert isinstance(audio_array, np.ndarray)
        assert sample_rate == 16000
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()