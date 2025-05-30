#!/usr/bin/env python3
"""
Integrated Voice Assistant - "Ziggy"
Combines all tested components into a complete voice assistant

Features:
- Custom "ziggy" wake word detection using Vosk
- Smart query routing (local functions vs AI)
- GPU-accelerated AI responses via msty.app
- espeak text-to-speech output with interruption capability
- Enhanced web search (read results or open browser)
- Auto-start capability with welcome message
- "take a break" command to gracefully shutdown
- Local-first privacy protection

Usage: python3 voice_assistant.py
Dependencies: vosk, pyaudio, requests
"""

import json
import os
import re
import subprocess
import time
import tempfile
import signal
import sys
import threading
import queue
import urllib.parse
from datetime import datetime
from pathlib import Path

import requests
import vosk
import pyaudio
import wave


class VoiceAssistant:
    def __init__(self):
        # Configuration
        self.wake_word = "ziggy"
        self.shutdown_phrase = "take a break"
        self.is_listening = True
        self.is_processing = False
        self.conversational_mode = False  # Track if we're in a conversation
        self.conversation_history = []  # Store conversation context
        
        # Backend configuration
        self.backend_type = None  # 'msty' or 'ollama'
        self.backend_url = None
        self.backend_name = None
        self.backend_process = None  # Store process if we start it
        self.msty_url = "http://localhost:10000"
        self.ollama_url = "http://localhost:11434"

        # Audio configuration
        self.sample_rate = 16000
        self.chunk_size = 4000
        self.channels = 1
        self.format = pyaudio.paInt16

        # Initialize components
        self.audio = None
        self.vosk_model = None
        self.default_model = None
        self.setup_successful = False

        print("🤖 Initializing Ziggy Voice Assistant...")
        self.setup_components()

    def setup_components(self):
        """Initialize all voice assistant components"""
        try:
            # Initialize audio system
            self.audio = pyaudio.PyAudio()
            print("✅ Audio system initialized")

            # Load Vosk model
            model_paths = [
                Path("vosk-model-small-en-us-0.15"),
                Path("vosk-model-en-us-0.22"),
                Path("vosk-model-en-us-0.22-lgraph"),
            ]

            model_path = None
            for path in model_paths:
                if path.exists():
                    model_path = str(path)
                    break

            if not model_path:
                print("❌ No Vosk model found. Please download:")
                print("wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
                print("unzip vosk-model-small-en-us-0.15.zip")
                return

            self.vosk_model = vosk.Model(model_path)
            print("✅ Speech recognition model loaded")

            # Detect and setup AI backend
            if not self.setup_ai_backend():
                return

            # Get default model for the backend
            if not self.get_default_model():
                return

            # Test text-to-speech
            # First try Piper
            self.piper_available = False
            self.piper_path = os.path.expanduser("~/.local/share/piper/piper/piper")
            self.piper_model = os.path.expanduser("~/.local/share/piper/en_US-amy-medium.onnx")
            
            if os.path.exists(self.piper_path) and os.path.exists(self.piper_model):
                try:
                    # Test Piper
                    result = subprocess.run(
                        [self.piper_path, "--version"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        self.piper_available = True
                        print("✅ Piper TTS ready (natural voice)")
                except Exception:
                    pass
            
            # Fallback to espeak
            if not self.piper_available:
                try:
                    result = subprocess.run(['which', 'espeak'], capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✅ Text-to-speech system ready (using espeak)")
                    else:
                        print("❌ No TTS system found - install espeak or set up Piper")
                        return
                except Exception as e:
                    print(f"❌ Text-to-speech error: {e}")
                    return

            self.setup_successful = True
            print("🎉 All systems ready!")

        except Exception as e:
            print(f"❌ Setup failed: {e}")
            self.setup_successful = False

    def check_backend_running(self, url, backend_type):
        """Check if a backend is running at the given URL"""
        try:
            if backend_type == "msty":
                # First check if it's actually Ollama serving OpenAI-compatible API
                try:
                    ollama_check = requests.get(f"{url}/api/tags", timeout=1)
                    if ollama_check.status_code == 200:
                        # It's Ollama, not Msty
                        return False
                except:
                    pass
                
                # Now check for Msty
                response = requests.get(f"{url}/v1/models", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    # Check for model ownership pattern - Ollama uses "library", Msty doesn't
                    if 'data' in data and data['data']:
                        # Check if this is Ollama masquerading as OpenAI API
                        first_model = data['data'][0]
                        if first_model.get('owned_by') == 'library':
                            return False  # This is Ollama, not Msty
                        return True  # This is likely Msty
                    return False
            else:  # ollama
                response = requests.get(f"{url}/api/tags", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    return 'models' in data
            return False
        except:
            return False

    def start_backend(self, backend_type):
        """Start the specified backend"""
        try:
            if backend_type == "msty":
                print("🚀 Starting Msty backend...")
                # Check if msty command exists
                result = subprocess.run(['which', 'msty'], capture_output=True, text=True)
                if result.returncode != 0:
                    print("❌ Msty not found. Please install it first.")
                    return False
                
                # Start msty serve in background
                self.backend_process = subprocess.Popen(
                    ['msty', 'serve'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
            else:  # ollama
                print("🚀 Starting Ollama backend...")
                # Check if ollama command exists
                result = subprocess.run(['which', 'ollama'], capture_output=True, text=True)
                if result.returncode != 0:
                    print("❌ Ollama not found. Please install it first.")
                    return False
                
                # Start ollama serve in background
                self.backend_process = subprocess.Popen(
                    ['ollama', 'serve'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            # Wait for backend to be ready (up to 30 seconds)
            url = self.msty_url if backend_type == "msty" else self.ollama_url
            for i in range(30):
                time.sleep(1)
                if self.check_backend_running(url, backend_type):
                    print(f"✅ {backend_type.capitalize()} backend started successfully")
                    return True
                if i % 5 == 0:
                    print(f"⏳ Waiting for {backend_type} to start... ({i+1}/30)")
            
            print(f"❌ {backend_type.capitalize()} failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Error starting {backend_type}: {e}")
            return False

    def setup_ai_backend(self):
        """Detect running AI backend or start one"""
        print("🔍 Detecting AI backends...")
        
        # Check if Msty is running
        print(f"   Checking Msty at {self.msty_url}...")
        if self.check_backend_running(self.msty_url, "msty"):
            self.backend_type = "msty"
            self.backend_url = self.msty_url
            self.backend_name = "Msty"
            print(f"✅ Connected to Msty backend")
            return True
        
        # Check if Ollama is running
        print(f"   Checking Ollama at {self.ollama_url}...")
        if self.check_backend_running(self.ollama_url, "ollama"):
            self.backend_type = "ollama"
            self.backend_url = self.ollama_url
            self.backend_name = "Ollama"
            print(f"✅ Connected to Ollama backend")
            return True
        
        # No backend running - ask user which to start
        print("❌ No AI backend detected")
        
        # Use espeak to ask since we haven't fully initialized yet
        ask_text = "No AI backend detected. Would you like me to start Misty or Ollama?"
        subprocess.run([
            'espeak',
            '-s', '150',
            '-v', 'en',
            ask_text
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Record user response
        print("🎤 Listening for your choice...")
        audio_data = self.record_backend_choice()
        if not audio_data:
            print("❌ No response detected")
            return False
        
        # Convert to text
        choice_text = self.speech_to_text(audio_data)
        if not choice_text:
            print("❌ Couldn't understand response")
            return False
        
        print(f"📝 You said: '{choice_text}'")
        choice_lower = choice_text.lower()
        
        # Parse choice
        if "msty" in choice_lower or "misty" in choice_lower:
            backend_choice = "msty"
        elif "ollama" in choice_lower:
            backend_choice = "ollama"
        else:
            # Ask again with clearer options
            clarify_text = "I didn't catch that. Please say 'Misty' or 'Ollama'"
            subprocess.run([
                'espeak',
                '-s', '150',
                '-v', 'en',
                clarify_text
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            audio_data = self.record_backend_choice()
            if not audio_data:
                return False
            
            choice_text = self.speech_to_text(audio_data)
            choice_lower = choice_text.lower()
            
            if "msty" in choice_lower or "misty" in choice_lower:
                backend_choice = "msty"
            elif "ollama" in choice_lower:
                backend_choice = "ollama"
            else:
                print("❌ Could not determine backend choice")
                return False
        
        # Start the chosen backend
        if self.start_backend(backend_choice):
            if backend_choice == "msty":
                self.backend_type = "msty"
                self.backend_url = self.msty_url
                self.backend_name = "Msty"
            else:
                self.backend_type = "ollama"
                self.backend_url = self.ollama_url
                self.backend_name = "Ollama"
            
            # Announce connection
            announce_text = f"Successfully connected to {self.backend_name}"
            subprocess.run([
                'espeak',
                '-s', '150',
                '-v', 'en',
                announce_text
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return True
        
        return False

    def record_backend_choice(self):
        """Simple recording for backend choice - before full init"""
        try:
            if not self.audio:
                self.audio = pyaudio.PyAudio()
            
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            # Record for 3 seconds
            for _ in range(0, int(self.sample_rate / self.chunk_size * 3)):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
            
            stream.close()
            return b''.join(frames)
            
        except Exception as e:
            print(f"Recording error: {e}")
            return None

    def get_default_model(self):
        """Get the default model for the current backend"""
        try:
            if self.backend_type == "msty":
                response = requests.get(f"{self.backend_url}/v1/models", timeout=5)
                if response.status_code == 200:
                    models_data = response.json()
                    if 'data' in models_data and models_data['data']:
                        self.default_model = models_data['data'][0]['id']
                        print(f"✅ Using model: {self.default_model}")
                        return True
                    else:
                        self.default_model = "llama3.2:latest"
                        print(f"✅ Using fallback model: {self.default_model}")
                        return True
            else:  # ollama
                response = requests.get(f"{self.backend_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models_data = response.json()
                    if 'models' in models_data and models_data['models']:
                        self.default_model = models_data['models'][0]['name']
                        print(f"✅ Using model: {self.default_model}")
                        return True
                    else:
                        self.default_model = "llama2"
                        print(f"✅ Using fallback model: {self.default_model}")
                        return True
                        
            print("❌ Could not get model list from backend")
            return False
                
        except Exception as e:
            print(f"❌ Error getting models: {e}")
            return False

    def query_backend(self, messages, temperature=0.7, max_tokens=500):
        """Unified interface to query either backend"""
        try:
            if self.backend_type == "msty":
                # Msty uses OpenAI-compatible API
                payload = {
                    "model": self.default_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                response = requests.post(
                    f"{self.backend_url}/v1/chat/completions",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
                    
            else:  # ollama
                # Ollama uses its own API format
                # Convert messages to Ollama format
                prompt = ""
                for msg in messages:
                    if msg['role'] == 'system':
                        prompt += f"System: {msg['content']}\n"
                    elif msg['role'] == 'user':
                        prompt += f"User: {msg['content']}\n"
                    elif msg['role'] == 'assistant':
                        prompt += f"Assistant: {msg['content']}\n"
                prompt += "Assistant: "
                
                payload = {
                    "model": self.default_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/generate",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['response'].strip()
            
            return None
            
        except Exception as e:
            print(f"Backend query error: {e}")
            return None

    def speak(self, text, allow_interruption=True):
        """Convert text to speech with optional interruption capability"""
        try:
            print(f"🗣️ Speaking: {text}")

            if not allow_interruption or len(text) < 100:
                # Short responses - speak normally without interruption
                if self.piper_available:
                    # Use Piper for natural voice
                    # Escape single quotes in text
                    escaped_text = text.replace("'", "'\"'\"'")
                    process = subprocess.Popen(
                        f"echo '{escaped_text}' | {self.piper_path} --model {self.piper_model} --output-raw",
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL
                    )
                    # Play the audio
                    play_process = subprocess.Popen(
                        ['aplay', '-r', '22050', '-f', 'S16_LE', '-t', 'raw', '-'],
                        stdin=process.stdout,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    play_process.wait()
                else:
                    # Fallback to espeak
                    subprocess.run([
                        'espeak',
                        '-s', '150',  # Speed (words per minute)
                        '-v', 'en',  # Voice (English)
                        text
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return False  # Not interrupted

            # Long responses - enable interruption
            return self.speak_with_interruption(text)

        except Exception as e:
            print(f"Speech error: {e}")
            return False

    def speak_with_interruption(self, text):
        """Speak text while listening for 'ziggy' interruption"""
        try:
            # Break text into sentences for chunked speaking
            sentences = self.split_into_sentences(text)

            # Setup interruption detection
            interruption_queue = queue.Queue()
            stop_speaking = threading.Event()

            # Start listening for interruption in background
            listener_thread = threading.Thread(
                target=self.listen_for_interruption,
                args=(interruption_queue, stop_speaking)
            )
            listener_thread.daemon = True
            listener_thread.start()

            # Speak each sentence, checking for interruption
            for i, sentence in enumerate(sentences):
                if stop_speaking.is_set():
                    print("🛑 Speech interrupted by wake word")
                    break

                # Speak this sentence
                if self.piper_available:
                    # Use Piper
                    # Escape single quotes in sentence
                    escaped_sentence = sentence.strip().replace("'", "'\"'\"'")
                    piper_process = subprocess.Popen(
                        f"echo '{escaped_sentence}' | {self.piper_path} --model {self.piper_model} --output-raw",
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL
                    )
                    process = subprocess.Popen(
                        ['aplay', '-r', '22050', '-f', 'S16_LE', '-t', 'raw', '-'],
                        stdin=piper_process.stdout,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    # Use espeak
                    process = subprocess.Popen([
                        'espeak',
                        '-s', '150',
                        '-v', 'en',
                        sentence.strip()
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # Wait for sentence to finish, checking for interruption
                while process.poll() is None:
                    if stop_speaking.is_set():
                        process.terminate()
                        print("🛑 Speech interrupted mid-sentence")
                        break
                    time.sleep(0.1)

            # Stop the listener
            stop_speaking.set()

            # Check if we were interrupted
            try:
                interruption_detected = interruption_queue.get_nowait()
                return True  # Was interrupted
            except queue.Empty:
                return False  # Completed normally

        except Exception as e:
            print(f"Interruptible speech error: {e}")
            return False

    def listen_for_interruption(self, interruption_queue, stop_event):
        """Listen for 'ziggy' wake word during speech"""
        try:
            # Create a separate recognizer for interruption detection
            recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)

            # Open audio stream for interruption detection
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            print("👂 Listening for interruption...")

            while not stop_event.is_set():
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)

                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        if result.get('text'):
                            transcript = result['text'].lower().strip()

                            # Check for wake word
                            if self.wake_word in transcript:
                                print(f"🎉 Interruption detected: '{transcript}'")
                                interruption_queue.put(True)
                                stop_event.set()
                                break

                except Exception as e:
                    if not stop_event.is_set():
                        print(f"Interruption listening error: {e}")
                        time.sleep(0.1)

            stream.close()

        except Exception as e:
            print(f"Interruption listener setup error: {e}")

    def split_into_sentences(self, text):
        """Split text into sentences for chunked speaking"""
        # Simple sentence splitting
        import re

        # Split on periods, exclamation marks, question marks
        sentences = re.split(r'[.!?]+', text)

        # Clean up and filter empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        # If no sentences found, return original text
        if not sentences:
            return [text]

        # Rejoin sentences that are too short (likely abbreviations)
        cleaned_sentences = []
        current_sentence = ""

        for sentence in sentences:
            current_sentence += sentence + ". "

            # If sentence is reasonable length or we're at the end, add it
            if len(current_sentence.split()) >= 5 or sentence == sentences[-1]:
                cleaned_sentences.append(current_sentence.strip())
                current_sentence = ""

        return cleaned_sentences if cleaned_sentences else [text]

    def contains_question(self, text):
        """Check if the text contains a question"""
        # Debug print
        print(f"🔍 Checking for question in: {text[:100]}...")
        
        # Check for question marks
        if '?' in text:
            print("   ✓ Found question mark")
            return True
        
        # Check for question words at the beginning of sentences
        question_starters = [
            'what', 'where', 'when', 'who', 'why', 'how',
            'would', 'could', 'should', 'can', 'will', 'do',
            'does', 'did', 'is', 'are', 'was', 'were',
            'have', 'has', 'had', 'may', 'might'
        ]
        
        # Split into sentences and check each
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip().lower()
            if any(sentence.startswith(word + ' ') for word in question_starters):
                print(f"   ✓ Found question starter: {sentence[:30]}...")
                return True
        
        print("   ✗ No question detected")
        return False

    def get_time(self):
        """Get current time - local function"""
        now = datetime.now()
        return f"The time is {now.strftime('%I:%M %p')}"

    def get_date(self):
        """Get current date - local function"""
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}"

    def handle_conversion(self, text):
        """Handle unit conversions - local function"""
        text_lower = text.lower()

        # Temperature conversion
        if 'celsius' in text_lower and 'fahrenheit' in text_lower:
            numbers = re.findall(r'-?\d+\.?\d*', text)
            if numbers:
                if 'celsius' in text_lower.split('fahrenheit')[0]:
                    # Celsius to Fahrenheit
                    celsius = float(numbers[0])
                    fahrenheit = (celsius * 9 / 5) + 32
                    return f"{celsius} degrees Celsius is {fahrenheit:.1f} degrees Fahrenheit"
                else:
                    # Fahrenheit to Celsius
                    fahrenheit = float(numbers[0])
                    celsius = (fahrenheit - 32) * 5 / 9
                    return f"{fahrenheit} degrees Fahrenheit is {celsius:.1f} degrees Celsius"

        # Distance conversion
        if 'feet' in text_lower and 'meters' in text_lower:
            numbers = re.findall(r'-?\d+\.?\d*', text)
            if numbers:
                if 'feet' in text_lower.split('meters')[0]:
                    # Feet to meters
                    feet = float(numbers[0])
                    meters = feet * 0.3048
                    return f"{feet} feet is {meters:.2f} meters"
                else:
                    # Meters to feet
                    meters = float(numbers[0])
                    feet = meters / 0.3048
                    return f"{meters} meters is {feet:.2f} feet"

        return None  # Conversion not handled locally

    def request_online_permission(self, query_type="search"):
        """Request explicit permission before any online activity"""
        permission_text = f"I cannot answer that from my local resources. Do you want me to check online?"

        # Enter conversational mode
        self.conversational_mode = True
        
        # Use non-interruptible speech for permission requests (they're short)
        self.speak(permission_text, allow_interruption=False)
        print(f"🌐 Requesting online permission for: {query_type}")

        # Record user response in conversational mode
        response_audio = self.record_command(duration=3, conversational=True)
        if response_audio:
            response_text = self.speech_to_text(response_audio)
            response_lower = response_text.lower().strip()

            # Check for affirmative responses
            affirmative_words = ['yes', 'yeah', 'yep', 'okay', 'ok', 'sure', 'go ahead', 'please']
            negative_words = ['no', 'nope', 'don\'t', 'stop', 'cancel', 'nevermind']

            if any(word in response_lower for word in affirmative_words):
                print(f"✅ Online permission granted")
                return True
            elif any(word in response_lower for word in negative_words):
                print(f"❌ Online permission denied")
                return False
            else:
                # Unclear response - err on side of caution
                print(f"⚠️ Unclear response - defaulting to no online access")
                return False
        else:
            print(f"❌ No response - defaulting to no online access")
            return False

    def web_search(self, query):
        """Enhanced web search - offers to read results or open browser"""
        # Request permission first
        if not self.request_online_permission("web search"):
            return "Okay, staying local. Is there anything else I can help you with?"

        # Offer two options
        options_text = "Would you like me to read you the answer, or open a browser window?"
        
        # Stay in conversational mode
        self.conversational_mode = True
        
        self.speak(options_text, allow_interruption=False)  # Short question
        print(f"🤔 Asking user preference: read vs browse")

        # Record user response in conversational mode
        response_audio = self.record_command(duration=4, conversational=True)
        if response_audio:
            response_text = self.speech_to_text(response_audio)
            response_lower = response_text.lower().strip()
            print(f"📝 User choice: '{response_text}'")

            # Check what user wants
            read_words = ['read', 'tell', 'say', 'speak', 'answer']
            browse_words = ['browser', 'open', 'window', 'firefox', 'chrome']

            if any(word in response_lower for word in read_words):
                print("📖 User chose: read results")
                return self.fetch_and_read_results(query)
            elif any(word in response_lower for word in browse_words):
                print("🌐 User chose: open browser")
                return self.open_browser_search(query)
            else:
                # Default to reading if unclear
                print("❓ Unclear response - defaulting to read results")
                return self.fetch_and_read_results(query)
        else:
            print("❌ No response - defaulting to read results")
            return self.fetch_and_read_results(query)

    def fetch_and_read_results(self, query):
        """Fetch web search results and read them aloud"""
        try:
            print(f"🔍 Searching for: {query}")
            self.speak("Let me search for that", allow_interruption=False)

            # Use DuckDuckGo instant answers API (privacy-focused)
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"

            response = requests.get(search_url, timeout=10)
            if response.status_code == 200:
                data = response.json()

                # Try to get a direct answer
                answer = data.get('AbstractText', '').strip()
                if not answer:
                    answer = data.get('Answer', '').strip()

                if answer:
                    # Clean up the answer for speech
                    clean_answer = answer.replace('\n', ' ').replace('  ', ' ')
                    # Limit length for speech
                    if len(clean_answer) > 300:
                        clean_answer = clean_answer[:300] + "... would you like me to open a browser for more details?"

                    print(f"📖 Found answer: {clean_answer}")
                    return clean_answer
                else:
                    # No direct answer found, offer browser instead
                    print("❓ No direct answer found")
                    fallback_msg = "I couldn't find a direct answer. Let me open a browser search for you."
                    self.speak(fallback_msg, allow_interruption=False)
                    time.sleep(1)  # Brief pause
                    return self.open_browser_search(query)
            else:
                print(f"❌ Search API error: {response.status_code}")
                return self.open_browser_search(query)

        except Exception as e:
            print(f"🔍 Search error: {e}")
            error_msg = "I had trouble searching. Let me open a browser for you instead."
            self.speak(error_msg, allow_interruption=False)
            time.sleep(1)
            return self.open_browser_search(query)

    def open_browser_search(self, query):
        """Open browser with search results"""
        try:
            print("🌐 Opening web browser...")
            # Use Popen to avoid blocking
            encoded_query = urllib.parse.quote_plus(query)
            subprocess.Popen(['firefox', f'https://duckduckgo.com/?q={encoded_query}'],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)

            # Give the browser time to start
            time.sleep(2)

            return f"Opened browser search for {query}"
        except Exception as e:
            print(f"Browser launch error: {e}")
            return "Could not open web browser"

    def query_ai_local_only(self, text):
        """Send query to local AI with explicit local-only instruction"""
        try:
            messages = [
                {"role": "system",
                 "content": "You are a local AI assistant. Answer questions using only your training data. If a question requires current information, real-time data, or internet searches, respond with exactly: 'I need online resources to answer that properly.'"},
                {"role": "user", "content": f"Please provide a brief, spoken response to: {text}"}
            ]
            
            ai_response = self.query_backend(messages, temperature=0.7, max_tokens=2000)
            
            if ai_response:
                # Check if AI indicates it needs online resources
                if "I need online resources" in ai_response:
                    if not self.request_online_permission("AI research with online context"):
                        return "Okay, I'll stick to what I know locally. Is there anything else I can help you with from my local knowledge?"

                    # Permission granted - send query without local-only restriction
                    return self.query_ai_unrestricted(text)

                return ai_response
            else:
                return "Sorry, I couldn't process that request"

        except Exception as e:
            print(f"AI query error: {e}")
            return "Sorry, there was an error processing your request"

    def query_ai_unrestricted(self, text):
        """Send query to AI without local-only restrictions (after permission granted)"""
        try:
            messages = [
                {"role": "user", "content": f"Please provide a brief, spoken response to: {text}"}
            ]
            
            ai_response = self.query_backend(messages, temperature=0.7, max_tokens=2000)
            
            if ai_response:
                return ai_response
            else:
                return "Sorry, I couldn't process that request"

        except Exception as e:
            print(f"AI query error: {e}")
            return "Sorry, there was an error processing your request"

    def estimate_tokens(self, text):
        """Rough estimate of token count (1 token ≈ 4 chars or 0.75 words)"""
        # Simple estimation: average of character and word-based counts
        char_estimate = len(text) / 4
        word_estimate = len(text.split()) / 0.75
        return int((char_estimate + word_estimate) / 2)
    
    def handle_conversational_response(self, text):
        """Handle responses during conversational mode with full context"""
        try:
            # Build messages with conversation history
            messages = [
                {"role": "system",
                 "content": "You are having a friendly conversation. Respond naturally and keep the conversation flowing. Feel free to ask follow-up questions or share related thoughts. Be engaging and personable."}
            ]
            
            # Dynamic context management based on token count
            max_context_tokens = 32000  # Conservative limit for Llama models
            system_tokens = self.estimate_tokens(messages[0]['content'])
            current_tokens = system_tokens + self.estimate_tokens(text)
            
            # Add conversation history, newest first, until we approach token limit
            for i in range(len(self.conversation_history) - 1, -1, -1):
                msg = self.conversation_history[i]
                msg_tokens = self.estimate_tokens(msg['content'])
                
                if current_tokens + msg_tokens > max_context_tokens - 2000:  # Leave room for response
                    print(f"💭 Context limit reached: including {len(self.conversation_history) - i} most recent messages")
                    break
                    
                messages.insert(1, msg)  # Insert after system message
                current_tokens += msg_tokens
            
            # Add the current user message
            messages.append({"role": "user", "content": text})
            
            print(f"📊 Context: {current_tokens} tokens, {len(messages)-1} messages from history")
            
            ai_response = self.query_backend(messages, temperature=0.8, max_tokens=2000)  # Allow longer responses
            
            if ai_response:
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": text})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                return ai_response
            else:
                return "Sorry, I couldn't process that response"

        except Exception as e:
            print(f"Conversational AI error: {e}")
            return "Sorry, there was an error continuing our conversation"

    def route_query(self, text):
        """Route query to appropriate handler"""
        text_lower = text.lower().strip()

        # Check for shutdown command
        if self.shutdown_phrase in text_lower:
            return "shutdown", "Okay, bye!"

        # Check for new conversation command
        if any(phrase in text_lower for phrase in ['new conversation', 'start over', 'clear history', 'fresh start']):
            self.conversation_history = []
            print("🧹 Cleared conversation history (user requested)")
            return "local", "Starting fresh. What would you like to talk about?"

        # Time queries
        if any(word in text_lower for word in ['time', 'clock', "what time"]):
            return "local", self.get_time()

        # Date queries
        if any(word in text_lower for word in ['date', 'today', "what day"]):
            return "local", self.get_date()

        # Unit conversions
        if 'convert' in text_lower or any(unit in text_lower for unit in [
            'celsius', 'fahrenheit', 'meters', 'feet', 'pounds', 'kilograms'
        ]):
            conversion_result = self.handle_conversion(text)
            if conversion_result:
                return "local", conversion_result

        # Web search
        if text_lower.startswith('search') or 'look up' in text_lower:
            query = text_lower.replace('search', '').replace('look up', '').strip()
            return "local", self.web_search(query)

        # Send to AI for complex queries (local-first with permission model)
        return "ai", self.query_ai_local_only(text)

    def record_command(self, duration=5, conversational=False):
        """Record audio command until pause detected"""
        try:
            if conversational:
                print(f"💬 Listening for your response...")
            else:
                print(f"🎤 Recording until pause detected...")

            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            frames = []
            recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
            
            # Voice activity detection parameters
            silence_threshold = 1.5  # seconds of silence before stopping
            
            # Different limits for different modes
            if conversational:
                max_duration = 600  # 10 minutes for conversational responses
                initial_wait = 0.3  # Wait briefly for user to start speaking
                time.sleep(initial_wait)
            else:
                max_duration = 60  # 1 minute for initial commands
            
            last_speech_time = time.time()
            start_time = time.time()
            has_speech = False
            
            last_feedback_time = start_time
            
            while True:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Provide periodic feedback for long recordings
                if elapsed > 30 and (current_time - last_feedback_time) > 30:
                    minutes = int(elapsed / 60)
                    seconds = int(elapsed % 60)
                    print(f"⏱️ Recording: {minutes}:{seconds:02d} elapsed...")
                    last_feedback_time = current_time
                
                # Check for maximum duration
                if elapsed > max_duration:
                    print(f"⏱️ Maximum recording duration reached ({int(max_duration/60)} minutes)")
                    break
                
                # Read audio chunk
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Check for speech using Vosk's partial recognition
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if result.get('text'):
                        # Speech detected
                        last_speech_time = current_time
                        has_speech = True
                else:
                    # Check partial result for ongoing speech
                    partial = json.loads(recognizer.PartialResult())
                    if partial.get('partial'):
                        # Ongoing speech detected
                        last_speech_time = current_time
                        has_speech = True
                
                # Check for silence after speech
                if has_speech and (current_time - last_speech_time) > silence_threshold:
                    duration = current_time - start_time
                    if duration < 60:
                        print(f"🔇 Pause detected after {duration:.1f} seconds")
                    else:
                        minutes = int(duration / 60)
                        seconds = int(duration % 60)
                        print(f"🔇 Pause detected after {minutes}:{seconds:02d}")
                    break

            stream.close()
            
            # Return recorded audio
            if frames:
                return b''.join(frames)
            else:
                return None

        except Exception as e:
            print(f"Recording error: {e}")
            return None

    def speech_to_text(self, audio_data):
        """Convert audio data to text using Vosk"""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_filename = temp_file.name

            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)

            # Transcribe with Vosk
            recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
            results = []

            with wave.open(temp_filename, 'rb') as wf:
                while True:
                    data = wf.readframes(self.chunk_size)
                    if len(data) == 0:
                        break
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        if result.get('text'):
                            results.append(result['text'])

            # Get final result
            final_result = json.loads(recognizer.FinalResult())
            if final_result.get('text'):
                results.append(final_result['text'])

            # Cleanup
            Path(temp_filename).unlink(missing_ok=True)

            return ' '.join(results).strip()

        except Exception as e:
            print(f"Speech recognition error: {e}")
            return ""

    def listen_for_wake_word(self):
        """Continuously listen for the wake word 'ziggy' with auto-recovery"""
        max_retries = 3
        retry_count = 0

        while self.is_listening and retry_count < max_retries:
            try:
                recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)

                # Try to open audio stream with retry logic
                stream = None
                for attempt in range(3):
                    try:
                        stream = self.audio.open(
                            format=self.format,
                            channels=self.channels,
                            rate=self.sample_rate,
                            input=True,
                            frames_per_buffer=self.chunk_size
                        )
                        break
                    except Exception as e:
                        print(f"Audio stream attempt {attempt + 1} failed: {e}")
                        time.sleep(1)  # Wait before retry

                if not stream:
                    print("❌ Could not open audio stream")
                    return False

                print(f"👂 Listening for wake word '{self.wake_word}'...")
                retry_count = 0  # Reset retry count on successful stream open

                while self.is_listening:
                    try:
                        data = stream.read(self.chunk_size, exception_on_overflow=False)

                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            if result.get('text'):
                                transcript = result['text'].lower().strip()

                                # Check for wake word
                                if self.wake_word in transcript:
                                    print(f"🎉 Wake word detected: '{transcript}'")
                                    stream.close()
                                    return True  # Wake word found

                                # Check for shutdown command
                                if self.shutdown_phrase in transcript:
                                    print(f"🛑 Shutdown command detected: '{transcript}'")
                                    stream.close()
                                    return "shutdown"

                    except Exception as e:
                        if self.is_listening:
                            print(f"⚠️ Audio read error: {e}")
                            # Break inner loop to retry stream setup
                            break

                if stream:
                    stream.close()
                return False

            except Exception as e:
                retry_count += 1
                print(f"🔄 Wake word detection error (attempt {retry_count}): {e}")
                if retry_count < max_retries:
                    print(f"Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print("❌ Max retries reached for audio stream")
                    return False

        return False

    def handle_voice_command(self):
        """Handle complete voice interaction after wake word"""
        try:
            self.is_processing = True
            self.conversational_mode = False  # Reset at start of new interaction
            
            # Check if we should clear conversation history (after timeout or explicit new conversation)
            # Clear history if it's been more than 5 minutes since last interaction
            if hasattr(self, 'last_interaction_time'):
                if time.time() - self.last_interaction_time > 300:  # 5 minutes
                    self.conversation_history = []
                    print("🧹 Cleared conversation history (timeout)")
            
            self.last_interaction_time = time.time()
            
            self.speak("Yes?", allow_interruption=False)  # Short acknowledgment

            # Record the user's command
            audio_data = self.record_command()
            if not audio_data:
                self.speak("I didn't hear anything", allow_interruption=False)
                return

            # Convert speech to text
            command_text = self.speech_to_text(audio_data)
            if not command_text:
                self.speak("I couldn't understand that", allow_interruption=False)
                return

            print(f"📝 Command: '{command_text}'")

            # Route and process the command
            route_type, response = self.route_query(command_text)

            if route_type == "shutdown":
                self.speak(response, allow_interruption=False)
                self.shutdown()
                return

            # Store initial exchange in conversation history
            if route_type == "ai":
                self.conversation_history.append({"role": "user", "content": command_text})
                self.conversation_history.append({"role": "assistant", "content": response})

            # Speak the response with interruption capability for long responses
            was_interrupted = self.speak(response, allow_interruption=True)

            if was_interrupted:
                print("🔄 Response was interrupted - processing new command")
                # Speech was interrupted by "ziggy" - handle the new command
                self.handle_voice_command()
                return
            else:
                print(f"✅ Response delivered completely")

            # Check if the response contains a question
            if self.contains_question(response):
                print("❓ Response contains a question - entering conversational mode")
                self.conversational_mode = True
                
                # Listen for the answer
                answer_audio = self.record_command(conversational=True)
                if answer_audio:
                    answer_text = self.speech_to_text(answer_audio)
                    if answer_text:
                        print(f"📝 User answered: '{answer_text}'")
                        
                        # Check for shutdown in conversation
                        if self.shutdown_phrase in answer_text.lower():
                            self.speak("Okay, bye!", allow_interruption=False)
                            self.shutdown()
                            return
                        
                        # Process the answer as a conversational follow-up - NOT through route_query!
                        follow_up_response = self.handle_conversational_response(answer_text)
                        
                        # Speak the follow-up response and check if it contains another question
                        was_interrupted = self.speak(follow_up_response, allow_interruption=True)
                        
                        if not was_interrupted and self.contains_question(follow_up_response):
                            # Continue the conversation if AI asks another question
                            print("🔄 Continuing conversation...")
                            # Don't reset everything - just continue listening
                            continue_conversation = True
                            while continue_conversation:
                                answer_audio = self.record_command(conversational=True)
                                if answer_audio:
                                    answer_text = self.speech_to_text(answer_audio)
                                    if answer_text:
                                        print(f"📝 User answered: '{answer_text}'")
                                        
                                        # Check for shutdown
                                        if self.shutdown_phrase in answer_text.lower():
                                            self.speak("Okay, bye!", allow_interruption=False)
                                            self.shutdown()
                                            return
                                        
                                        # Continue the conversation
                                        follow_up_response = self.handle_conversational_response(answer_text)
                                        was_interrupted = self.speak(follow_up_response, allow_interruption=True)
                                        
                                        # Check if we should continue
                                        if was_interrupted or not self.contains_question(follow_up_response):
                                            continue_conversation = False
                                else:
                                    continue_conversation = False

            # Add a small pause to ensure audio operations complete
            time.sleep(0.5)

            # For web operations, add extra recovery time
            if 'browser' in response.lower() or 'search' in response.lower():
                print("🔄 Allowing extra time for browser operations...")
                time.sleep(1.5)

        except Exception as e:
            print(f"Command handling error: {e}")
            self.speak("Sorry, I had trouble processing that", allow_interruption=False)
        finally:
            self.is_processing = False
            self.conversational_mode = False  # Reset conversational mode
            print("👂 Ready to listen for wake word again...")

    def startup_message(self):
        """Play welcome message on startup"""
        welcome_msg = f"Welcome. Ziggy is ready to assist you, connected to {self.backend_name} with extended conversation support."
        print(f"🤖 {welcome_msg}")
        self.speak(welcome_msg, allow_interruption=False)

    def shutdown(self):
        """Gracefully shutdown the voice assistant"""
        print("🛑 Shutting down Ziggy...")
        self.is_listening = False
        
        # Handle backend process if we started one
        if self.backend_process:
            # Ask if we should keep it running
            keep_text = f"Should I keep {self.backend_name} running after I shut down?"
            self.speak(keep_text, allow_interruption=False)
            
            # Record response
            audio_data = self.record_backend_choice()
            if audio_data:
                response_text = self.speech_to_text(audio_data)
                response_lower = response_text.lower().strip()
                
                # Check for affirmative
                if any(word in response_lower for word in ['yes', 'yeah', 'yep', 'keep', 'leave']):
                    print(f"✅ Leaving {self.backend_name} running")
                else:
                    print(f"🛑 Stopping {self.backend_name}...")
                    self.backend_process.terminate()
                    try:
                        self.backend_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.backend_process.kill()
                    print(f"✅ {self.backend_name} stopped")
            else:
                # No response - default to leaving it running
                print(f"✅ Leaving {self.backend_name} running (no response)")
        
        if self.audio:
            self.audio.terminate()
        print("👋 Goodbye!")
        sys.exit(0)

    def run(self):
        """Main run loop for the voice assistant"""
        if not self.setup_successful:
            print("❌ Setup failed - cannot start voice assistant")
            return

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, lambda s, f: self.shutdown())
        signal.signal(signal.SIGTERM, lambda s, f: self.shutdown())

        # Play startup message
        self.startup_message()

        print(f"\n🎯 Voice Assistant Active")
        print(f"Wake word: '{self.wake_word}'")
        print(f"Shutdown: '{self.shutdown_phrase}'")
        print(f"Press Ctrl+C to stop")
        print("-" * 50)

        try:
            while self.is_listening:
                # Listen for wake word
                wake_result = self.listen_for_wake_word()

                if wake_result == "shutdown":
                    self.speak("Okay, bye!", allow_interruption=False)
                    self.shutdown()
                elif wake_result == True:
                    # Wake word detected - handle command
                    self.handle_voice_command()
                elif not self.is_listening:
                    # Shutdown requested
                    break

                # Brief pause before resuming listening
                if self.is_listening:
                    time.sleep(0.1)

        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            print(f"Main loop error: {e}")
            self.shutdown()


def main():
    print("🤖 Ziggy Voice Assistant")
    print("Local-first AI assistant with privacy protection")
    print("=" * 50)

    # Create and run the voice assistant
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()