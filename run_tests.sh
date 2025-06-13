#!/bin/bash

# Run tests for the voice assistant

echo "🧪 Running Voice Assistant Tests..."
echo "=================================="

# Activate virtual environment if it exists
if [ -d "voice_assistant_env" ]; then
    echo "📦 Activating virtual environment..."
    source voice_assistant_env/bin/activate
fi

# Install test dependencies if needed
if ! pip show pytest > /dev/null 2>&1; then
    echo "📥 Installing test dependencies..."
    pip install -r requirements-test.txt
fi

# Run tests with coverage
echo "🏃 Running tests with coverage..."
pytest

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed!"
    exit 1
fi

echo ""
echo "📊 Coverage report generated in htmlcov/"