# Changelog

## [Unreleased] - Conversational Mode Features

### Added
- **Dynamic Voice Activity Detection**: System now listens until a pause is detected instead of fixed 5-second recording
  - Configurable silence threshold (1.5 seconds)
  - Maximum recording duration safety limit (30 seconds)
  - Real-time speech detection using Vosk partial recognition

- **Conversational Mode**: Automatic listening after clarifying questions
  - System detects when it asks a question and automatically listens for response
  - No wake word required during conversational exchanges
  - Smooth back-and-forth dialogue flow

- **Conversation Context Tracking**: Full conversation history with context-aware responses
  - Maintains conversation history across exchanges
  - AI receives last 10 exchanges for better context understanding
  - Automatic history clearing after 5 minutes of inactivity
  - Manual conversation reset with commands like "new conversation" or "start over"

- **Question Detection**: Intelligent detection of questions in AI responses
  - Checks for question marks and common question starter words
  - Automatically enters conversational mode when questions are detected

### Changed
- **Token Limits**: Increased AI response token limits from 150 to 500
  - Prevents mid-sentence cutoffs
  - Allows complete, coherent responses
  - Maintains "brief" instruction for voice-appropriate length

- **Recording Feedback**: Enhanced user feedback during recording
  - Different messages for normal vs conversational recording
  - Clear indication of recording status and mode

### Technical Improvements
- Added `conversational_mode` flag to track conversation state
- Added `conversation_history` list for context maintenance
- Added `handle_conversational_response()` method for context-aware AI queries
- Added `contains_question()` method for intelligent question detection
- Modified `record_command()` to support conversational parameter
- Enhanced `handle_voice_command()` to support recursive conversation flow

### User Experience
- More natural conversation flow without repeated wake word usage
- Better context retention across multiple exchanges
- Ability to have extended conversations with proper context
- Clearer feedback about system state and listening mode