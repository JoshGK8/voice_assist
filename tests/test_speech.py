"""
Unit tests for speech module
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import json
import numpy as np
from speech.interfaces import (
    SpeechRecognitionInterface,
    TextToSpeechInterface,
    WakeWordDetectorInterface
)
from speech.factory import SpeechFactory


class TestSpeechInterfaces:
    """Test speech interfaces"""
    
    def test_speech_recognition_interface(self):
        """Test SpeechRecognitionInterface is abstract"""
        with pytest.raises(TypeError):
            SpeechRecognitionInterface()
    
    def test_text_to_speech_interface(self):
        """Test TextToSpeechInterface is abstract"""
        with pytest.raises(TypeError):
            TextToSpeechInterface()
    
    def test_wake_word_detector_interface(self):
        """Test WakeWordDetectorInterface is abstract"""
        with pytest.raises(TypeError):
            WakeWordDetectorInterface()


class TestSpeechFactory:
    """Test SpeechFactory"""
    
    @patch('speech.vosk_impl.vosk.Model')
    def test_create_recognizer(self, mock_vosk_model):
        """Test creating speech recognizer"""
        mock_vosk_model.return_value = MagicMock()
        
        recognizer = SpeechFactory.create_recognizer(
            backend="vosk",
            model_path="/path/to/model"
        )
        assert recognizer is not None
        assert hasattr(recognizer, 'recognize')
        assert hasattr(recognizer, 'is_ready')
    
    def test_create_recognizer_no_model_path(self):
        """Test error when no model path provided"""
        with pytest.raises(ValueError, match="model_path required"):
            SpeechFactory.create_recognizer(backend="vosk")
    
    def test_create_tts_espeak(self):
        """Test creating espeak TTS"""
        tts = SpeechFactory.create_tts(backend="espeak")
        assert tts is not None
        assert hasattr(tts, 'speak')
        assert hasattr(tts, 'speak_async')
        assert hasattr(tts, 'stop_speaking')
        assert hasattr(tts, 'is_speaking')
    
    @patch('speech.tts_impl.os.path.exists')
    def test_create_tts_piper(self, mock_exists):
        """Test creating piper TTS"""
        mock_exists.return_value = True
        
        tts = SpeechFactory.create_tts(
            backend="piper",
            piper_path="/path/to/piper",
            model_path="/path/to/model"
        )
        assert tts is not None
    
    @patch('speech.vosk_impl.vosk.Model')
    def test_create_wake_word_detector(self, mock_vosk_model):
        """Test creating wake word detector"""
        mock_vosk_model.return_value = MagicMock()
        
        detector = SpeechFactory.create_wake_word_detector(
            backend="vosk",
            model_path="/path/to/model",
            wake_word="ziggy"
        )
        assert detector is not None
        assert hasattr(detector, 'detect')
        assert hasattr(detector, 'get_wake_word')
        assert hasattr(detector, 'set_wake_word')


class TestVoskSpeechRecognition:
    """Test Vosk speech recognition implementation"""
    
    @patch('speech.vosk_impl.vosk.KaldiRecognizer')
    @patch('speech.vosk_impl.vosk.Model')
    def test_initialization(self, mock_model, mock_recognizer):
        """Test Vosk recognizer initialization"""
        from speech.vosk_impl import VoskSpeechRecognition
        
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        
        recognizer = VoskSpeechRecognition("/path/to/model")
        
        mock_model.assert_called_once_with("/path/to/model")
        mock_recognizer.assert_called_once_with(mock_model_instance, 16000)
        assert recognizer.is_ready()
    
    @patch('speech.vosk_impl.vosk.KaldiRecognizer')
    @patch('speech.vosk_impl.vosk.Model')
    def test_recognize_final_result(self, mock_model, mock_recognizer_class):
        """Test recognizing speech with final result"""
        from speech.vosk_impl import VoskSpeechRecognition
        
        mock_recognizer = MagicMock()
        mock_recognizer.AcceptWaveform.return_value = True
        mock_recognizer.Result.return_value = json.dumps({"text": "hello world"})
        mock_recognizer_class.return_value = mock_recognizer
        
        recognizer = VoskSpeechRecognition("/path/to/model")
        result = recognizer.recognize(b'audio_data')
        
        assert result == "hello world"
        mock_recognizer.AcceptWaveform.assert_called_once_with(b'audio_data')
    
    @patch('speech.vosk_impl.vosk.KaldiRecognizer')
    @patch('speech.vosk_impl.vosk.Model')
    def test_recognize_partial_result(self, mock_model, mock_recognizer_class):
        """Test recognizing speech with partial result"""
        from speech.vosk_impl import VoskSpeechRecognition
        
        mock_recognizer = MagicMock()
        mock_recognizer.AcceptWaveform.return_value = False
        mock_recognizer.PartialResult.return_value = json.dumps({"partial": "hello"})
        mock_recognizer_class.return_value = mock_recognizer
        
        recognizer = VoskSpeechRecognition("/path/to/model")
        result = recognizer.recognize(b'audio_data')
        
        assert result == "hello"
        mock_recognizer.AcceptWaveform.assert_called_once_with(b'audio_data')
    
    @patch('speech.vosk_impl.vosk.KaldiRecognizer')
    @patch('speech.vosk_impl.vosk.Model')
    def test_recognize_numpy_array(self, mock_model, mock_recognizer_class):
        """Test recognizing speech from numpy array"""
        from speech.vosk_impl import VoskSpeechRecognition
        
        mock_recognizer = MagicMock()
        mock_recognizer.AcceptWaveform.return_value = True
        mock_recognizer.Result.return_value = json.dumps({"text": "test"})
        mock_recognizer_class.return_value = mock_recognizer
        
        audio_array = np.zeros(1000, dtype=np.int16)
        
        recognizer = VoskSpeechRecognition("/path/to/model")
        result = recognizer.recognize(audio_array)
        
        assert result == "test"
        # Check that numpy array was converted to bytes
        mock_recognizer.AcceptWaveform.assert_called_once()
        call_args = mock_recognizer.AcceptWaveform.call_args[0][0]
        assert isinstance(call_args, bytes)


class TestVoskWakeWordDetector:
    """Test Vosk wake word detector implementation"""
    
    @patch('speech.vosk_impl.vosk.KaldiRecognizer')
    @patch('speech.vosk_impl.vosk.Model')
    def test_detect_wake_word_present(self, mock_model, mock_recognizer_class):
        """Test detecting wake word when present"""
        from speech.vosk_impl import VoskWakeWordDetector
        
        mock_recognizer = MagicMock()
        mock_recognizer.AcceptWaveform.return_value = True
        mock_recognizer.Result.return_value = json.dumps({"text": "hey ziggy"})
        mock_recognizer_class.return_value = mock_recognizer
        
        detector = VoskWakeWordDetector("/path/to/model", wake_word="ziggy")
        detected = detector.detect(b'audio_data')
        
        assert detected is True
    
    @patch('speech.vosk_impl.vosk.KaldiRecognizer')
    @patch('speech.vosk_impl.vosk.Model')
    def test_detect_wake_word_absent(self, mock_model, mock_recognizer_class):
        """Test detecting wake word when absent"""
        from speech.vosk_impl import VoskWakeWordDetector
        
        mock_recognizer = MagicMock()
        mock_recognizer.AcceptWaveform.return_value = True
        mock_recognizer.Result.return_value = json.dumps({"text": "hello world"})
        mock_recognizer_class.return_value = mock_recognizer
        
        detector = VoskWakeWordDetector("/path/to/model", wake_word="ziggy")
        detected = detector.detect(b'audio_data')
        
        assert detected is False
    
    @patch('speech.vosk_impl.vosk.Model')
    def test_get_set_wake_word(self, mock_model):
        """Test getting and setting wake word"""
        from speech.vosk_impl import VoskWakeWordDetector
        
        detector = VoskWakeWordDetector("/path/to/model", wake_word="ziggy")
        
        assert detector.get_wake_word() == "ziggy"
        
        detector.set_wake_word("Alexa")
        assert detector.get_wake_word() == "alexa"  # Should be lowercase


class TestEspeakTTS:
    """Test Espeak TTS implementation"""
    
    @patch('speech.tts_impl.subprocess.Popen')
    def test_speak(self, mock_popen):
        """Test speaking text"""
        from speech.tts_impl import EspeakTTS
        
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        tts = EspeakTTS()
        tts.speak("Hello world")
        
        import subprocess
        mock_popen.assert_called_once_with(
            ['espeak', '-s', '150', '-v', 'en', 'Hello world'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        mock_process.wait.assert_called_once()
    
    @patch('speech.tts_impl.threading.Thread')
    def test_speak_async(self, mock_thread):
        """Test async speaking"""
        from speech.tts_impl import EspeakTTS
        
        tts = EspeakTTS()
        tts.speak_async("Hello")
        
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    @patch('speech.tts_impl.subprocess.Popen')
    def test_stop_speaking(self, mock_popen):
        """Test stopping speech"""
        from speech.tts_impl import EspeakTTS
        
        mock_process = MagicMock()
        
        tts = EspeakTTS()
        tts.current_process = mock_process
        tts.is_speaking_flag = True
        
        tts.stop_speaking()
        
        mock_process.terminate.assert_called_once()
        assert tts.is_speaking_flag is False
        assert tts.current_process is None
    
    @patch('speech.tts_impl.subprocess.run')
    @patch('speech.tts_impl.tempfile.NamedTemporaryFile')
    def test_get_audio_data(self, mock_tempfile, mock_run):
        """Test getting audio data"""
        from speech.tts_impl import EspeakTTS
        
        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.wav'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        # Mock file reading
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = b'audio_data'
            
            tts = EspeakTTS()
            data = tts.get_audio_data("Test")
            
            assert data == b'audio_data'
            mock_run.assert_called_once()


class TestPiperTTS:
    """Test Piper TTS implementation"""
    
    @patch('speech.tts_impl.os.path.exists')
    def test_initialization(self, mock_exists):
        """Test Piper TTS initialization"""
        from speech.tts_impl import PiperTTS
        
        mock_exists.return_value = True
        
        tts = PiperTTS("/path/to/piper", "/path/to/model")
        assert tts.available is True
        
        mock_exists.return_value = False
        tts = PiperTTS("/invalid/path", "/invalid/model")
        assert tts.available is False
    
    @patch('speech.tts_impl.subprocess.Popen')
    @patch('speech.tts_impl.os.path.exists')
    def test_speak(self, mock_exists, mock_popen):
        """Test Piper speaking"""
        from speech.tts_impl import PiperTTS
        
        mock_exists.return_value = True
        mock_process1 = MagicMock()
        mock_process2 = MagicMock()
        mock_popen.side_effect = [mock_process1, mock_process2]
        
        tts = PiperTTS("/path/to/piper", "/path/to/model")
        tts.speak("Hello world")
        
        assert mock_popen.call_count == 2
        mock_process2.wait.assert_called_once()
    
    @patch('speech.tts_impl.os.path.exists')
    def test_speak_not_available(self, mock_exists):
        """Test speaking when Piper not available"""
        from speech.tts_impl import PiperTTS
        
        mock_exists.return_value = False
        
        tts = PiperTTS("/path/to/piper", "/path/to/model")
        
        with pytest.raises(RuntimeError, match="Piper TTS not available"):
            tts.speak("Hello")