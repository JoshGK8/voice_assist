from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class AIModel:
    """Represents an AI model"""
    name: str
    size: Optional[str] = None
    context_length: Optional[int] = None


@dataclass
class AIResponse:
    """Response from AI backend"""
    content: str
    model: str
    tokens_used: Optional[int] = None
    error: Optional[str] = None


class AIBackendInterface(ABC):
    """Interface for AI backend operations"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the backend is available"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[AIModel]:
        """List available models"""
        pass
    
    @abstractmethod
    def query(self, prompt: str, model: Optional[str] = None,
             context: Optional[List[Dict[str, str]]] = None,
             stream: bool = False) -> AIResponse:
        """Query the AI backend"""
        pass
    
    @abstractmethod
    def get_backend_name(self) -> str:
        """Get the name of the backend"""
        pass
    
    @abstractmethod
    def get_backend_url(self) -> str:
        """Get the URL of the backend"""
        pass


class AIBackendManagerInterface(ABC):
    """Interface for managing AI backends"""
    
    @abstractmethod
    def detect_backend(self) -> Optional[str]:
        """Detect which backend is running"""
        pass
    
    @abstractmethod
    def start_backend(self, backend_type: str) -> bool:
        """Start a specific backend"""
        pass
    
    @abstractmethod
    def stop_backend(self) -> None:
        """Stop the running backend"""
        pass
    
    @abstractmethod
    def get_backend(self) -> Optional[AIBackendInterface]:
        """Get the current backend instance"""
        pass