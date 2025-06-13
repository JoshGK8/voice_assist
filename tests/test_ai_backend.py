"""
Unit tests for AI backend module
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from ai.interfaces import (
    AIBackendInterface,
    AIBackendManagerInterface,
    AIModel,
    AIResponse
)
from ai.backend_manager import AIBackendManager
from ai.ollama_backend import OllamaBackend
from ai.msty_backend import MstyBackend


class TestAIInterfaces:
    """Test AI interfaces"""
    
    def test_ai_backend_interface(self):
        """Test AIBackendInterface is abstract"""
        with pytest.raises(TypeError):
            AIBackendInterface()
    
    def test_ai_backend_manager_interface(self):
        """Test AIBackendManagerInterface is abstract"""
        with pytest.raises(TypeError):
            AIBackendManagerInterface()
    
    def test_ai_model_dataclass(self):
        """Test AIModel dataclass"""
        model = AIModel(name="test-model", size="7B", context_length=4096)
        assert model.name == "test-model"
        assert model.size == "7B"
        assert model.context_length == 4096
    
    def test_ai_response_dataclass(self):
        """Test AIResponse dataclass"""
        response = AIResponse(
            content="Hello",
            model="test-model",
            tokens_used=10,
            error=None
        )
        assert response.content == "Hello"
        assert response.model == "test-model"
        assert response.tokens_used == 10
        assert response.error is None


class TestOllamaBackend:
    """Test Ollama backend implementation"""
    
    @patch('ai.ollama_backend.requests.get')
    def test_is_available_true(self, mock_get):
        """Test when Ollama is available"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        backend = OllamaBackend()
        assert backend.is_available() is True
        mock_get.assert_called_with("http://localhost:11434/api/tags", timeout=2)
    
    @patch('ai.ollama_backend.requests.get')
    def test_is_available_false(self, mock_get):
        """Test when Ollama is not available"""
        mock_get.side_effect = Exception("Connection error")
        
        backend = OllamaBackend()
        assert backend.is_available() is False
    
    @patch('ai.ollama_backend.requests.get')
    def test_list_models(self, mock_get):
        """Test listing models"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:7b", "size": 3825819904},
                {"name": "mistral:latest", "size": 4109916160}
            ]
        }
        mock_get.return_value = mock_response
        
        backend = OllamaBackend()
        models = backend.list_models()
        
        assert len(models) == 2
        assert models[0].name == "llama2:7b"
        assert models[0].size == "3.6GB"
        assert models[1].name == "mistral:latest"
        assert models[1].size == "3.8GB"
    
    @patch('ai.ollama_backend.requests.post')
    @patch('ai.ollama_backend.requests.get')
    def test_query_success(self, mock_get, mock_post):
        """Test successful query"""
        # Mock list_models for default model selection
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "models": [{"name": "llama2:7b", "size": 3825819904}]
        }
        mock_get.return_value = mock_get_response
        
        # Mock query response
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "message": {"content": "Hello, I am an AI assistant."},
            "total_duration": 1234567890
        }
        mock_post.return_value = mock_post_response
        
        backend = OllamaBackend()
        response = backend.query("Hello")
        
        assert response.content == "Hello, I am an AI assistant."
        assert response.model == "llama2:7b"
        assert response.tokens_used == 1234567890
        assert response.error is None
    
    @patch('ai.ollama_backend.requests.post')
    def test_query_with_context(self, mock_post):
        """Test query with context"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Based on context..."}
        }
        mock_post.return_value = mock_response
        
        backend = OllamaBackend()
        context = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Previous question"}
        ]
        response = backend.query("New question", model="llama2", context=context)
        
        # Verify the request included context
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert len(call_args[1]['json']['messages']) == 3  # context + new message
    
    def test_format_size(self):
        """Test size formatting"""
        backend = OllamaBackend()
        assert backend._format_size(500) == "500.0B"
        assert backend._format_size(1500) == "1.5KB"
        assert backend._format_size(1500000) == "1.4MB"
        assert backend._format_size(1500000000) == "1.4GB"


class TestMstyBackend:
    """Test Msty backend implementation"""
    
    @patch('ai.msty_backend.requests.get')
    def test_is_available_true(self, mock_get):
        """Test when Msty is available"""
        # First call checks for Ollama (should fail)
        mock_ollama_response = MagicMock()
        mock_ollama_response.status_code = 404
        
        # Second call checks for Msty
        mock_msty_response = MagicMock()
        mock_msty_response.status_code = 200
        mock_msty_response.json.return_value = {
            "data": [{"id": "gpt-4", "owned_by": "openai"}]
        }
        
        mock_get.side_effect = [Exception(), mock_msty_response]
        
        backend = MstyBackend()
        assert backend.is_available() is True
    
    @patch('ai.msty_backend.requests.get')
    def test_is_available_false_when_ollama(self, mock_get):
        """Test when it's actually Ollama pretending to be Msty"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        backend = MstyBackend()
        assert backend.is_available() is False
    
    @patch('ai.msty_backend.requests.get')
    def test_list_models(self, mock_get):
        """Test listing Msty models"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "gpt-4", "context_length": 8192},
                {"id": "claude-3", "context_length": 100000}
            ]
        }
        mock_get.return_value = mock_response
        
        backend = MstyBackend()
        models = backend.list_models()
        
        assert len(models) == 2
        assert models[0].name == "gpt-4"
        assert models[0].context_length == 8192
        assert models[1].name == "claude-3"
        assert models[1].context_length == 100000
    
    @patch('ai.msty_backend.requests.post')
    def test_query_success(self, mock_post):
        """Test successful Msty query"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {"content": "Hello from Msty!"}
            }],
            "usage": {"total_tokens": 42}
        }
        mock_post.return_value = mock_response
        
        backend = MstyBackend()
        response = backend.query("Hello", model="gpt-4")
        
        assert response.content == "Hello from Msty!"
        assert response.model == "gpt-4"
        assert response.tokens_used == 42
        assert response.error is None


class TestAIBackendManager:
    """Test AI backend manager"""
    
    @patch('ai.backend_manager.MstyBackend')
    @patch('ai.backend_manager.OllamaBackend')
    def test_detect_backend_msty(self, mock_ollama_class, mock_msty_class):
        """Test detecting Msty backend"""
        mock_msty = MagicMock()
        mock_msty.is_available.return_value = True
        mock_msty_class.return_value = mock_msty
        
        manager = AIBackendManager()
        backend_type = manager.detect_backend()
        
        assert backend_type == "msty"
        assert manager.current_backend == mock_msty
        assert manager.current_backend_type == "msty"
    
    @patch('ai.backend_manager.MstyBackend')
    @patch('ai.backend_manager.OllamaBackend')
    def test_detect_backend_ollama(self, mock_ollama_class, mock_msty_class):
        """Test detecting Ollama backend"""
        mock_msty = MagicMock()
        mock_msty.is_available.return_value = False
        mock_msty_class.return_value = mock_msty
        
        mock_ollama = MagicMock()
        mock_ollama.is_available.return_value = True
        mock_ollama_class.return_value = mock_ollama
        
        manager = AIBackendManager()
        backend_type = manager.detect_backend()
        
        assert backend_type == "ollama"
        assert manager.current_backend == mock_ollama
        assert manager.current_backend_type == "ollama"
    
    @patch('ai.backend_manager.subprocess.run')
    @patch('ai.backend_manager.subprocess.Popen')
    @patch('ai.backend_manager.MstyBackend')
    def test_start_backend_msty(self, mock_msty_class, mock_popen, mock_run):
        """Test starting Msty backend"""
        # Mock 'which msty' command
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock backend process
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        # Mock backend availability
        mock_backend = MagicMock()
        mock_backend.is_available.side_effect = [False, False, True]  # Available on 3rd check
        mock_msty_class.return_value = mock_backend
        
        manager = AIBackendManager()
        
        with patch('time.sleep'):  # Speed up test
            success = manager.start_backend("msty")
        
        assert success is True
        assert manager.current_backend == mock_backend
        assert manager.backend_process == mock_process
        import subprocess
        mock_popen.assert_called_once_with(
            ['msty', 'serve'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    @patch('ai.backend_manager.subprocess.run')
    def test_start_backend_not_installed(self, mock_run):
        """Test starting backend when not installed"""
        mock_run.return_value = MagicMock(returncode=1)
        
        manager = AIBackendManager()
        success = manager.start_backend("msty")
        
        assert success is False
    
    def test_stop_backend(self):
        """Test stopping backend"""
        manager = AIBackendManager()
        
        # Mock a running backend
        mock_process = MagicMock()
        manager.backend_process = mock_process
        manager.current_backend = MagicMock()
        manager.current_backend_type = "msty"
        
        manager.stop_backend()
        
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once_with(timeout=5)
        assert manager.backend_process is None
        assert manager.current_backend is None
        assert manager.current_backend_type is None
    
    def test_get_backend(self):
        """Test getting current backend"""
        manager = AIBackendManager()
        
        assert manager.get_backend() is None
        
        mock_backend = MagicMock()
        manager.current_backend = mock_backend
        
        assert manager.get_backend() == mock_backend