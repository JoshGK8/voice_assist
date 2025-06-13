import re
from typing import List, Tuple
from .interfaces import CommandHandlerInterface, CommandRouterInterface, CommandResult


class CommandRouter(CommandRouterInterface):
    """Routes commands to appropriate handlers"""
    
    def __init__(self):
        self.handlers: List[CommandHandlerInterface] = []
    
    def register_handler(self, handler: CommandHandlerInterface) -> None:
        """Register a command handler"""
        self.handlers.append(handler)
    
    def route_command(self, text: str) -> Tuple[str, CommandResult]:
        """Route command to appropriate handler"""
        # Try local handlers first
        for handler in self.handlers:
            if handler.can_handle(text):
                result = handler.handle(text)
                return "local", result
        
        # If no local handler can process it, return AI routing
        return "ai", CommandResult(
            response="",
            command_type="ai_query",
            metadata={"original_text": text}
        )
    
    def contains_question(self, text: str) -> bool:
        """Check if text contains a question"""
        # Check for question marks
        if '?' in text:
            return True
        
        # Check for question words at the beginning of sentences
        question_words = [
            'what', 'where', 'when', 'why', 'how', 'who', 'which', 'whose',
            'can', 'could', 'would', 'should', 'will', 'do', 'does', 'did',
            'is', 'are', 'was', 'were', 'am'
        ]
        
        # Split into sentences and check each one
        sentences = re.split(r'[.!]', text.lower())
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Split into words and check first word
            words = sentence.split()
            if words and words[0] in question_words:
                return True
        
        return False