from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ConversationMessage:
    """Single message in a conversation"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConversationContext:
    """Context for AI conversation"""
    messages: List[Dict[str, str]]
    token_count: int
    conversation_id: Optional[str] = None


class ConversationManagerInterface(ABC):
    """Interface for managing conversation state and context"""
    
    @abstractmethod
    def start_conversation(self) -> str:
        """Start a new conversation and return conversation ID"""
        pass
    
    @abstractmethod
    def add_message(self, role: str, content: str, conversation_id: Optional[str] = None) -> None:
        """Add a message to the conversation history"""
        pass
    
    @abstractmethod
    def get_context(self, max_tokens: int, conversation_id: Optional[str] = None) -> ConversationContext:
        """Get conversation context within token limit"""
        pass
    
    @abstractmethod
    def clear_history(self, conversation_id: Optional[str] = None) -> None:
        """Clear conversation history"""
        pass
    
    @abstractmethod
    def is_conversational_mode(self) -> bool:
        """Check if currently in conversational mode"""
        pass
    
    @abstractmethod
    def enter_conversational_mode(self) -> None:
        """Enter conversational mode"""
        pass
    
    @abstractmethod
    def exit_conversational_mode(self) -> None:
        """Exit conversational mode"""
        pass
    
    @abstractmethod
    def should_clear_history(self, timeout_seconds: int = 300) -> bool:
        """Check if history should be cleared due to timeout"""
        pass
    
    @abstractmethod
    def get_history_length(self, conversation_id: Optional[str] = None) -> int:
        """Get number of messages in history"""
        pass