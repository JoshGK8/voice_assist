import requests
import json
from typing import Dict, List, Optional
from .interfaces import AIBackendInterface, AIModel, AIResponse


class MstyBackend(AIBackendInterface):
    """Msty AI backend implementation"""
    
    def __init__(self, base_url: str = "http://localhost:10002"):
        self.base_url = base_url.rstrip('/')
        self.backend_name = "Msty"
    
    def is_available(self) -> bool:
        """Check if the backend is available"""
        try:
            # First check if it's Ollama masquerading
            try:
                ollama_check = requests.get(f"{self.base_url}/api/tags", timeout=2)
                if ollama_check.status_code == 200:
                    # It's Ollama, not Msty
                    return False
            except:
                pass
            
            # Now check for Msty
            response = requests.get(f"{self.base_url}/v1/models", timeout=2)
            if response.status_code == 200:
                data = response.json()
                # Check for model ownership pattern - Ollama uses "library", Msty doesn't
                if 'data' in data and data['data']:
                    # Check if this is Ollama masquerading as OpenAI API
                    first_model = data['data'][0]
                    if first_model.get('owned_by') == 'library':
                        return False  # This is Ollama, not Msty
                    return True  # This is likely Msty
                return False
            return False
        except:
            return False
    
    def list_models(self) -> List[AIModel]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model_data in data.get('data', []):
                    model = AIModel(
                        name=model_data.get('id', ''),
                        context_length=model_data.get('context_length')
                    )
                    models.append(model)
                return models
            return []
        except Exception as e:
            print(f"Error listing Msty models: {e}")
            return []
    
    def query(self, prompt: str, model: Optional[str] = None,
             context: Optional[List[Dict[str, str]]] = None,
             stream: bool = False) -> AIResponse:
        """Query the AI backend"""
        try:
            if not model:
                models = self.list_models()
                if not models:
                    return AIResponse(
                        content="",
                        model="",
                        error="No models available"
                    )
                model = models[0].name
            
            # Build messages
            messages = []
            if context:
                messages.extend(context)
            messages.append({"role": "user", "content": prompt})
            
            # Make request using OpenAI-compatible API
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                choices = data.get('choices', [])
                if choices:
                    return AIResponse(
                        content=choices[0].get('message', {}).get('content', ''),
                        model=model,
                        tokens_used=data.get('usage', {}).get('total_tokens')
                    )
                else:
                    return AIResponse(
                        content="",
                        model=model,
                        error="No response from model"
                    )
            else:
                return AIResponse(
                    content="",
                    model=model,
                    error=f"API error: {response.status_code}"
                )
                
        except Exception as e:
            return AIResponse(
                content="",
                model=model or "",
                error=str(e)
            )
    
    def get_backend_name(self) -> str:
        """Get the name of the backend"""
        return self.backend_name
    
    def get_backend_url(self) -> str:
        """Get the URL of the backend"""
        return self.base_url