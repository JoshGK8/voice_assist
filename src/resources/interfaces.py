from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ResourceProfile:
    """Resource profile configuration"""
    name: str
    description: str
    requirements: str
    context_tokens: int
    history_limit: int
    response_tokens: int
    recording_conversational: int  # seconds
    recording_command: int  # seconds


@dataclass
class MemoryStatus:
    """Memory usage information"""
    total: int  # MB
    used: int   # MB
    available: int  # MB
    percent: float


class ResourceManagerInterface(ABC):
    """Interface for resource management"""
    
    @abstractmethod
    def detect_gpu_memory(self) -> int:
        """Detect available GPU memory in MB"""
        pass
    
    @abstractmethod
    def get_profiles(self) -> Dict[str, ResourceProfile]:
        """Get all available resource profiles"""
        pass
    
    @abstractmethod
    def get_current_profile(self) -> Optional[ResourceProfile]:
        """Get the current active profile"""
        pass
    
    @abstractmethod
    def switch_profile(self, profile_name: str) -> bool:
        """Switch to a different profile"""
        pass
    
    @abstractmethod
    def auto_select_profile(self) -> ResourceProfile:
        """Auto-select profile based on available resources"""
        pass
    
    @abstractmethod
    def get_memory_status(self) -> MemoryStatus:
        """Get current memory usage status"""
        pass