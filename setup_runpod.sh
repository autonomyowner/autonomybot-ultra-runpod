#!/bin/bash
# RunPod deployment script for AutonomyBot Ultra

echo "🚀 Setting up AutonomyBot Ultra on RunPod..."

# Update system
apt-get update && apt-get install -y curl git

# Install Node.js (required for web projects)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install Python dependencies
pip install -r requirements.txt

# Install Ollama (if not already available)
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Start Ollama service in background
ollama serve &
sleep 10

# Pull required models (adjust based on GPU memory)
echo "Pulling AI models..."
ollama pull qwen2.5-coder:14b  # Good for 24GB VRAM
# ollama pull qwen2.5-coder:32b  # For 48GB+ VRAM
# ollama pull deepseek-coder:6.7b  # For 16GB VRAM

echo "✅ Setup complete! Run: python autonomydz_improved.py"
