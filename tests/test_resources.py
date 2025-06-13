"""
Unit tests for resources module
"""
import pytest
from unittest.mock import patch, MagicMock
from resources.manager import ResourceManager


class TestResourceManager:
    """Test resource manager"""
    
    @patch('resources.manager.subprocess.run')
    def test_detect_gpu_memory_nvidia(self, mock_run):
        """Test NVIDIA GPU memory detection"""
        # Mock nvidia-smi output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="8192, 2048\n"
        )
        
        manager = ResourceManager()
        available_memory = manager.detect_gpu_memory()
        
        # Should return 8192 - 2048 = 6144 MB
        assert available_memory == 6144
        import subprocess
        mock_run.assert_called_with([
            'nvidia-smi', 
            '--query-gpu=memory.total,memory.used', 
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True, stderr=subprocess.DEVNULL)
    
    @patch('resources.manager.subprocess.run')
    @patch('resources.manager.psutil')
    def test_detect_gpu_memory_fallback(self, mock_psutil, mock_run):
        """Test fallback to system RAM estimation"""
        # Mock nvidia-smi failure
        mock_run.side_effect = FileNotFoundError()
        
        # Mock system RAM
        mock_memory = MagicMock()
        mock_memory.total = 16 * 1024 * 1024 * 1024  # 16GB in bytes
        mock_psutil.virtual_memory.return_value = mock_memory
        
        manager = ResourceManager()
        available_memory = manager.detect_gpu_memory()
        
        # Should return 16GB / 8 = 2GB = 2048MB
        assert available_memory == 2048
    
    def test_get_profiles(self):
        """Test getting all profiles"""
        manager = ResourceManager()
        profiles = manager.get_profiles()
        
        assert "minimal" in profiles
        assert "standard" in profiles
        assert "performance" in profiles
        
        minimal = profiles["minimal"]
        assert minimal.name == "Minimal"
        assert minimal.context_tokens == 8000
        assert minimal.history_limit == 10
    
    @patch.object(ResourceManager, 'detect_gpu_memory')
    def test_auto_select_profile_minimal(self, mock_detect):
        """Test auto-selecting minimal profile for low memory"""
        mock_detect.return_value = 4096  # 4GB
        
        manager = ResourceManager()
        profile = manager.auto_select_profile()
        
        assert profile.name == "Minimal"
        assert manager.current_profile_name == "minimal"
    
    @patch.object(ResourceManager, 'detect_gpu_memory')
    def test_auto_select_profile_standard(self, mock_detect):
        """Test auto-selecting standard profile for medium memory"""
        mock_detect.return_value = 12288  # 12GB
        
        manager = ResourceManager()
        profile = manager.auto_select_profile()
        
        assert profile.name == "Standard"
        assert manager.current_profile_name == "standard"
    
    @patch.object(ResourceManager, 'detect_gpu_memory')
    def test_auto_select_profile_performance(self, mock_detect):
        """Test auto-selecting performance profile for high memory"""
        mock_detect.return_value = 20480  # 20GB
        
        manager = ResourceManager()
        profile = manager.auto_select_profile()
        
        assert profile.name == "Performance"
        assert manager.current_profile_name == "performance"
    
    def test_switch_profile_valid(self):
        """Test switching to valid profile"""
        manager = ResourceManager()
        
        success = manager.switch_profile("performance")
        assert success is True
        assert manager.current_profile_name == "performance"
        
        profile = manager.get_current_profile()
        assert profile.name == "Performance"
    
    def test_switch_profile_alias(self):
        """Test switching using profile alias"""
        manager = ResourceManager()
        
        success = manager.switch_profile("gaming")
        assert success is True
        assert manager.current_profile_name == "minimal"
        
        success = manager.switch_profile("high")
        assert success is True
        assert manager.current_profile_name == "performance"
    
    def test_switch_profile_invalid(self):
        """Test switching to invalid profile"""
        manager = ResourceManager()
        
        success = manager.switch_profile("nonexistent")
        assert success is False
        # Should not change current profile
    
    def test_get_memory_status(self):
        """Test getting memory status"""
        manager = ResourceManager()
        manager.available_memory = 8192  # 8GB
        manager.current_profile_name = "standard"
        
        status = manager.get_memory_status()
        
        assert status.used == 4000  # Expected for standard profile
        assert status.total == 8192 + 4000
        assert status.available == 8192
        assert 0 <= status.percent <= 100
    
    def test_get_profile_info(self):
        """Test getting profile information"""
        manager = ResourceManager()
        manager.available_memory = 8192
        manager.current_profile_name = "standard"
        
        info = manager.get_profile_info()
        
        assert "Standard mode" in info
        assert "gigabytes" in info
        assert "conversation exchanges" in info
        assert "minutes" in info
    
    def test_list_available_profiles(self):
        """Test listing available profiles"""
        manager = ResourceManager()
        manager.current_profile_name = "standard"
        
        profile_list = manager.list_available_profiles()
        
        assert "Available profiles:" in profile_list
        assert "Minimal:" in profile_list
        assert "Standard (current):" in profile_list
        assert "Performance:" in profile_list