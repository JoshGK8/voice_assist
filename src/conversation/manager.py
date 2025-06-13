import time
import uuid
from typing import List, Dict, Optional
from .interfaces import (
    ConversationManagerInterface, 
    ConversationMessage, 
    ConversationContext
)


class ConversationManager(ConversationManagerInterface):
    """Manages conversation state and context"""
    
    def __init__(self, history_limit: int = 20):
        self.history_limit = history_limit
        self.conversations: Dict[str, List[ConversationMessage]] = {}
        self.current_conversation_id: Optional[str] = None
        self.conversational_mode = False
        self.last_interaction_time = time.time()
        
    def start_conversation(self) -> str:
        """Start a new conversation and return conversation ID"""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = []
        self.current_conversation_id = conversation_id
        self.last_interaction_time = time.time()
        return conversation_id
    
    def add_message(self, role: str, content: str, conversation_id: Optional[str] = None) -> None:
        """Add a message to the conversation history"""
        if conversation_id is None:
            conversation_id = self.current_conversation_id
            
        if conversation_id is None:
            conversation_id = self.start_conversation()
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=time.time()
        )
        
        self.conversations[conversation_id].append(message)
        self.last_interaction_time = time.time()
        
        # Maintain history limit
        if len(self.conversations[conversation_id]) > self.history_limit * 2:
            # Keep most recent messages
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.history_limit * 2:]
    
    def get_context(self, max_tokens: int, conversation_id: Optional[str] = None) -> ConversationContext:
        """Get conversation context within token limit"""
        if conversation_id is None:
            conversation_id = self.current_conversation_id
            
        if conversation_id is None or conversation_id not in self.conversations:
            return ConversationContext(messages=[], token_count=0, conversation_id=conversation_id)
        
        messages = []
        current_tokens = 0
        
        # Process messages in reverse order (newest first)
        conversation_messages = self.conversations[conversation_id]
        
        for message in reversed(conversation_messages):
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            message_tokens = self._estimate_tokens(message.content)
            
            if current_tokens + message_tokens > max_tokens - 2000:  # Leave room for response
                break
            
            messages.insert(0, {
                "role": message.role,
                "content": message.content
            })
            current_tokens += message_tokens
        
        return ConversationContext(
            messages=messages,
            token_count=current_tokens,
            conversation_id=conversation_id
        )
    
    def clear_history(self, conversation_id: Optional[str] = None) -> None:
        """Clear conversation history"""
        if conversation_id is None:
            conversation_id = self.current_conversation_id
            
        if conversation_id and conversation_id in self.conversations:
            self.conversations[conversation_id] = []
            print("🧹 Cleared conversation history")
    
    def is_conversational_mode(self) -> bool:
        """Check if currently in conversational mode"""
        return self.conversational_mode
    
    def enter_conversational_mode(self) -> None:
        """Enter conversational mode"""
        self.conversational_mode = True
        print("💬 Entering conversational mode")
    
    def exit_conversational_mode(self) -> None:
        """Exit conversational mode"""
        self.conversational_mode = False
        print("🔚 Exiting conversational mode")
    
    def should_clear_history(self, timeout_seconds: int = 300) -> bool:
        """Check if history should be cleared due to timeout"""
        return time.time() - self.last_interaction_time > timeout_seconds
    
    def get_history_length(self, conversation_id: Optional[str] = None) -> int:
        """Get number of messages in history"""
        if conversation_id is None:
            conversation_id = self.current_conversation_id
            
        if conversation_id and conversation_id in self.conversations:
            return len(self.conversations[conversation_id])
        return 0
    
    def update_history_limit(self, new_limit: int) -> None:
        """Update history limit and trim if necessary"""
        self.history_limit = new_limit
        
        # Trim all conversations to new limit
        for conversation_id in self.conversations:
            if len(self.conversations[conversation_id]) > new_limit * 2:
                self.conversations[conversation_id] = self.conversations[conversation_id][-new_limit * 2:]
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Simple estimation: average of character and word-based counts
        char_estimate = len(text) / 4
        word_estimate = len(text.split()) / 0.75
        return int((char_estimate + word_estimate) / 2)
    
    def get_conversation_summary(self) -> str:
        """Get summary of current conversation"""
        if not self.current_conversation_id or self.current_conversation_id not in self.conversations:
            return "No active conversation"
        
        messages = self.conversations[self.current_conversation_id]
        if not messages:
            return "No messages in current conversation"
        
        user_messages = sum(1 for msg in messages if msg.role == "user")
        assistant_messages = sum(1 for msg in messages if msg.role == "assistant")
        
        return (
            f"Current conversation: {user_messages} user messages, "
            f"{assistant_messages} assistant responses"
        )