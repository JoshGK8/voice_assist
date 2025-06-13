from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of command execution"""
    response: str
    command_type: str
    success: bool = True
    metadata: Optional[Dict[str, Any]] = None


class CommandHandlerInterface(ABC):
    """Interface for command handlers"""
    
    @abstractmethod
    def can_handle(self, text: str) -> bool:
        """Check if this handler can process the given text"""
        pass
    
    @abstractmethod
    def handle(self, text: str) -> CommandResult:
        """Handle the command and return result"""
        pass
    
    @abstractmethod
    def get_command_type(self) -> str:
        """Get the type of commands this handler processes"""
        pass


class CommandRouterInterface(ABC):
    """Interface for command routing"""
    
    @abstractmethod
    def register_handler(self, handler: CommandHandlerInterface) -> None:
        """Register a command handler"""
        pass
    
    @abstractmethod
    def route_command(self, text: str) -> Tuple[str, CommandResult]:
        """Route command to appropriate handler"""
        pass
    
    @abstractmethod
    def contains_question(self, text: str) -> bool:
        """Check if text contains a question"""
        pass