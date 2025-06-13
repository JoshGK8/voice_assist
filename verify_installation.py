#!/usr/bin/env python3
"""
Installation verification script for Ziggy Voice Assistant
Run this to verify all dependencies are correctly installed.
"""

def test_core_dependencies():
    """Test core Python dependencies"""
    print("🔍 Testing core dependencies...")
    
    try:
        import pyaudio
        print(f"   ✅ PyAudio {pyaudio.__version__}")
    except ImportError as e:
        print(f"   ❌ PyAudio: {e}")
        return False
    
    try:
        import vosk
        print(f"   ✅ Vosk (speech recognition)")
    except ImportError as e:
        print(f"   ❌ Vosk: {e}")
        return False
    
    try:
        import pvporcupine
        print(f"   ✅ Porcupine (wake word detection)")
    except ImportError as e:
        print(f"   ❌ Porcupine: {e}")
        return False
    
    try:
        import requests
        print(f"   ✅ Requests {requests.__version__}")
    except ImportError as e:
        print(f"   ❌ Requests: {e}")
        return False
    
    try:
        import psutil
        print(f"   ✅ Psutil {psutil.__version__}")
    except ImportError as e:
        print(f"   ❌ Psutil: {e}")
        return False
    
    try:
        import numpy
        print(f"   ✅ NumPy {numpy.__version__}")
    except ImportError as e:
        print(f"   ❌ NumPy: {e}")
        return False
    
    return True


def test_modular_components():
    """Test our modular components"""
    print("\n🏗️ Testing modular components...")
    
    try:
        from src.audio import AudioFactory
        print("   ✅ Audio module")
    except ImportError as e:
        print(f"   ❌ Audio module: {e}")
        return False
    
    try:
        from src.speech import SpeechFactory
        print("   ✅ Speech module")
    except ImportError as e:
        print(f"   ❌ Speech module: {e}")
        return False
    
    try:
        from src.ai import AIBackendManager
        print("   ✅ AI module")
    except ImportError as e:
        print(f"   ❌ AI module: {e}")
        return False
    
    try:
        from src.commands import CommandRouter
        print("   ✅ Commands module")
    except ImportError as e:
        print(f"   ❌ Commands module: {e}")
        return False
    
    try:
        from src.conversation import ConversationManager
        print("   ✅ Conversation module")
    except ImportError as e:
        print(f"   ❌ Conversation module: {e}")
        return False
    
    try:
        from src.resources import ResourceManager
        print("   ✅ Resources module")
    except ImportError as e:
        print(f"   ❌ Resources module: {e}")
        return False
    
    return True


def test_voice_assistant():
    """Test main voice assistant"""
    print("\n🤖 Testing voice assistant...")
    
    try:
        from voice_assistant_clean import CleanVoiceAssistant
        print("   ✅ Clean voice assistant")
    except ImportError as e:
        print(f"   ❌ Clean voice assistant: {e}")
        return False
    
    try:
        # Test that we can instantiate (but don't run)
        assistant = CleanVoiceAssistant()
        print("   ✅ Voice assistant instantiation")
        return True
    except Exception as e:
        print(f"   ❌ Voice assistant instantiation: {e}")
        return False


def test_speech_model():
    """Test speech model availability"""
    print("\n🎤 Testing speech model...")
    
    import os
    model_path = "vosk-model-small-en-us-0.15"
    
    if os.path.exists(model_path):
        print(f"   ✅ Vosk model found at {model_path}")
        return True
    else:
        print(f"   ⚠️ Vosk model not found at {model_path}")
        print("   💡 Download with: wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        return False


def main():
    """Main verification function"""
    print("🚀 Ziggy Voice Assistant - Installation Verification")
    print("=" * 55)
    
    tests = [
        test_core_dependencies,
        test_modular_components,
        test_voice_assistant,
        test_speech_model
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All checks passed! Voice assistant is ready to use.")
        print("\n🏃 Quick start:")
        print("   python3 voice_assistant_clean.py")
    else:
        print("❌ Some checks failed. Please review the errors above.")
        if passed >= 3:  # Core deps + modules + assistant work
            print("💡 Core functionality should work, but some features may be limited.")
    
    return passed == total


if __name__ == "__main__":
    main()