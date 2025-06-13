"""
Integration tests that require real services
"""
import pytest
from ai.backend_manager import AIBackendManager
from ai.ollama_backend import OllamaBackend


@pytest.mark.integration
class TestOllamaIntegration:
    """Integration tests for Ollama backend"""
    
    def test_ollama_is_available(self):
        """Test real Ollama service is available"""
        backend = OllamaBackend()
        assert backend.is_available() is True
    
    def test_ollama_list_models(self):
        """Test listing real models from Ollama"""
        backend = OllamaBackend()
        models = backend.list_models()
        
        assert len(models) > 0
        assert any(model.name == "llama3.2:latest" for model in models)
        
        # Check model attributes
        for model in models:
            assert model.name
            assert model.size
    
    def test_ollama_query(self):
        """Test querying Ollama with a simple prompt"""
        backend = OllamaBackend()
        
        response = backend.query(
            prompt="Say hello in exactly three words",
            model="llama3.2:latest"
        )
        
        assert response.content
        assert response.model == "llama3.2:latest"
        assert response.error is None
        assert len(response.content.strip()) > 0
    
    def test_backend_manager_detect_ollama(self):
        """Test backend manager can detect running Ollama"""
        manager = AIBackendManager()
        backend_type = manager.detect_backend()
        
        assert backend_type == "ollama"
        assert manager.get_backend() is not None
        assert manager.get_backend().get_backend_name() == "Ollama"