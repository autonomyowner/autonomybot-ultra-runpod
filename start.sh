#!/bin/bash
# Start script for RunPod container

echo "🚀 Starting AutonomyBot Ultra on RunPod..."

# Start Ollama service
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    sleep 2
done

echo "✅ Ollama is ready!"

# Pull a default model if none exists
if ! ollama list | grep -q "qwen2.5-coder"; then
    echo "📥 Pulling default model..."
    # Use smaller model for faster startup
    ollama pull qwen2.5-coder:14b || ollama pull deepseek-coder:6.7b
fi

echo "🤖 Starting AutonomyBot Ultra..."

# Change to workspace directory
cd /workspace

# Start the main application
python /app/autonomydz_improved.py

# Cleanup on exit
trap "kill $OLLAMA_PID 2>/dev/null" EXIT
