"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def mock_audio_data():
    """Provide mock audio data for testing"""
    import numpy as np
    # Generate 1 second of silence at 16kHz
    return np.zeros(16000, dtype=np.int16)


@pytest.fixture
def mock_audio_bytes():
    """Provide mock audio bytes for testing"""
    import numpy as np
    return np.zeros(16000, dtype=np.int16).tobytes()