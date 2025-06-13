"""
Unit tests for conversation module
"""
import pytest
import time
from unittest.mock import patch
from conversation.manager import ConversationManager


class TestConversationManager:
    """Test conversation manager"""
    
    def test_start_conversation(self):
        """Test starting a new conversation"""
        manager = ConversationManager()
        conversation_id = manager.start_conversation()
        
        assert conversation_id is not None
        assert manager.current_conversation_id == conversation_id
        assert conversation_id in manager.conversations
        assert len(manager.conversations[conversation_id]) == 0
    
    def test_add_message(self):
        """Test adding messages to conversation"""
        manager = ConversationManager()
        conversation_id = manager.start_conversation()
        
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi there!")
        
        messages = manager.conversations[conversation_id]
        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"
        assert messages[1].role == "assistant"
        assert messages[1].content == "Hi there!"
    
    def test_add_message_auto_start_conversation(self):
        """Test auto-starting conversation when adding message"""
        manager = ConversationManager()
        
        manager.add_message("user", "Hello")
        
        assert manager.current_conversation_id is not None
        assert len(manager.conversations[manager.current_conversation_id]) == 1
    
    def test_get_context_empty(self):
        """Test getting context from empty conversation"""
        manager = ConversationManager()
        
        context = manager.get_context(max_tokens=1000)
        
        assert context.messages == []
        assert context.token_count == 0
        assert context.conversation_id is None
    
    def test_get_context_with_messages(self):
        """Test getting context with messages"""
        manager = ConversationManager()
        conversation_id = manager.start_conversation()
        
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi there!")
        manager.add_message("user", "How are you?")
        
        context = manager.get_context(max_tokens=1000)
        
        assert len(context.messages) == 3
        assert context.messages[0]["role"] == "user"
        assert context.messages[0]["content"] == "Hello"
        assert context.conversation_id == conversation_id
        assert context.token_count > 0
    
    def test_get_context_token_limit(self):
        """Test context token limiting"""
        manager = ConversationManager()
        conversation_id = manager.start_conversation()
        
        # Add many messages
        for i in range(10):
            manager.add_message("user", f"Message {i} " * 50)  # Long messages
            manager.add_message("assistant", f"Response {i} " * 50)
        
        # Request context with low token limit
        context = manager.get_context(max_tokens=100)
        
        # Should get fewer messages due to token limit
        assert len(context.messages) < 20  # Less than all 20 messages
        assert context.token_count <= 100 - 2000  # Within limit minus response buffer
    
    def test_clear_history(self):
        """Test clearing conversation history"""
        manager = ConversationManager()
        conversation_id = manager.start_conversation()
        
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi!")
        
        assert len(manager.conversations[conversation_id]) == 2
        
        manager.clear_history()
        
        assert len(manager.conversations[conversation_id]) == 0
    
    def test_conversational_mode(self):
        """Test conversational mode management"""
        manager = ConversationManager()
        
        assert manager.is_conversational_mode() is False
        
        manager.enter_conversational_mode()
        assert manager.is_conversational_mode() is True
        
        manager.exit_conversational_mode()
        assert manager.is_conversational_mode() is False
    
    def test_should_clear_history_timeout(self):
        """Test history timeout detection"""
        manager = ConversationManager()
        
        # Fresh manager should not need clearing
        assert manager.should_clear_history(timeout_seconds=300) is False
        
        # Simulate old interaction
        manager.last_interaction_time = time.time() - 400  # 400 seconds ago
        
        # Should need clearing now
        assert manager.should_clear_history(timeout_seconds=300) is True
    
    def test_get_history_length(self):
        """Test getting history length"""
        manager = ConversationManager()
        
        assert manager.get_history_length() == 0
        
        conversation_id = manager.start_conversation()
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi!")
        
        assert manager.get_history_length() == 2
    
    def test_update_history_limit(self):
        """Test updating history limit"""
        manager = ConversationManager(history_limit=5)
        conversation_id = manager.start_conversation()
        
        # Add many messages
        for i in range(15):
            manager.add_message("user", f"Message {i}")
        
        # Should be limited to 10 messages (5 * 2)
        assert len(manager.conversations[conversation_id]) == 10
        
        # Update limit
        manager.update_history_limit(2)
        
        # Should be trimmed to 4 messages (2 * 2)
        assert len(manager.conversations[conversation_id]) == 4
        assert manager.history_limit == 2
    
    def test_get_conversation_summary(self):
        """Test getting conversation summary"""
        manager = ConversationManager()
        
        # No conversation
        summary = manager.get_conversation_summary()
        assert "No active conversation" in summary
        
        # Empty conversation
        manager.start_conversation()
        summary = manager.get_conversation_summary()
        assert "No messages" in summary
        
        # With messages
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi!")
        manager.add_message("user", "How are you?")
        
        summary = manager.get_conversation_summary()
        assert "2 user messages" in summary
        assert "1 assistant responses" in summary
    
    def test_estimate_tokens(self):
        """Test token estimation"""
        manager = ConversationManager()
        
        # Test with known text
        tokens = manager._estimate_tokens("Hello world")
        assert tokens > 0
        assert tokens < 10  # Should be reasonable for short text
        
        # Longer text should have more tokens
        long_text = "This is a much longer piece of text that should have more tokens"
        long_tokens = manager._estimate_tokens(long_text)
        assert long_tokens > tokens
    
    def test_message_timestamps(self):
        """Test message timestamps"""
        manager = ConversationManager()
        conversation_id = manager.start_conversation()
        
        before_time = time.time()
        manager.add_message("user", "Hello")
        after_time = time.time()
        
        message = manager.conversations[conversation_id][0]
        assert message.timestamp is not None
        assert before_time <= message.timestamp <= after_time