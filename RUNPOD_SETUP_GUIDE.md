# 🚀 RUNPOD SETUP GUIDE FOR AUTONOMYBOT ULTRA

## ✅ STEP 1: YOUR CODE IS NOW ON GITHUB!
Repository: https://github.com/autonomyowner/autonomybot-ultra-runpod

## 🖥️ STEP 2: RUNPOD SETUP

### Create RunPod Account:
1. Go to https://runpod.io
2. Sign up with: autonomy.owner@gmail.com
3. Add payment method (required even for free tier)

### Deploy Pod:
1. Click "Deploy" → "GPU Pods"
2. **RECOMMENDED GPU**: RTX 4090 (24GB) - $0.34/hour
3. **Template**: Choose "RunPod Pytorch" or "RunPod Official"

### Pod Configuration:
```
Container Disk: 50 GB
Volume Disk: 20 GB
Expose HTTP Ports: 11434,3000,8080
Expose TCP Ports: 22
```

### Environment Variables:
```
OLLAMA_HOST=0.0.0.0:11434
NODE_ENV=development
WORKSPACE_DIR=/workspace
```

## 🔌 STEP 3: CONNECT TO YOUR POD

1. Once pod is running, click "Connect"
2. Choose "Start Web Terminal"
3. You'll get a terminal interface

## 📥 STEP 4: CLONE AND SETUP (Copy these commands)

```bash
# Navigate to workspace
cd /workspace

# Clone your repository
git clone https://github.com/autonomyowner/autonomybot-ultra-runpod.git

# Enter directory
cd autonomybot-ultra-runpod

# Make setup script executable
chmod +x setup_runpod.sh

# Run setup (this installs everything)
./setup_runpod.sh
```

## 🤖 STEP 5: START THE BOT

```bash
# Start the AutonomyBot
python autonomydz_improved.py
```

## 🌐 STEP 6: ACCESS YOUR APPS

Your pod will give you URLs like:
- Ollama API: https://YOUR_POD_ID-11434.proxy.runpod.net
- Dev Server: https://YOUR_POD_ID-3000.proxy.runpod.net

## 💡 QUICK TROUBLESHOOTING

If setup script fails, run manually:
```bash
# Install dependencies
pip install -r requirements.txt

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve &

# Pull AI model (for 24GB GPU)
ollama pull qwen2.5-coder:14b
```

## 💰 COST MANAGEMENT
- RTX 4090: ~$0.34/hour (~$8/day)
- ALWAYS terminate pods when not using
- Monitor usage in RunPod dashboard

## 🎯 YOU'RE READY!
1. ✅ Code pushed to GitHub
2. ✅ Setup guide ready
3. ✅ All configuration files included

Just follow the steps above in your RunPod terminal!
