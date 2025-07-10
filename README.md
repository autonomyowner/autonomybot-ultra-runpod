# AutonomyBot Ultra - RunPod Optimized

A next-generation conversational coding agent designed for cloud deployment on RunPod. This improved version features better resource management, async operations, enhanced error handling, and optimized performance for containerized environments.

## 🚀 Key Improvements

### RunPod Optimizations
- **Async Operations**: Non-blocking LLM calls and file operations
- **Resource Management**: Proper cleanup of processes and temporary files
- **Signal Handling**: Graceful shutdown on container termination
- **Memory Persistence**: State preservation across sessions
- **GPU-Aware Model Selection**: Automatic model selection based on available VRAM

### Enhanced Features
- **Project Templates**: Built-in templates for Next.js, React, Vite, and more
- **GitHub Integration**: Search repositories for inspiration
- **Enhanced Error Handling**: Robust error recovery and logging
- **Interactive Mode**: Real-time project modifications
- **Development Server**: Integrated dev server management
- **Git Automation**: Automatic repository setup and version control

### Performance Improvements
- **Model Fallback**: Automatic selection of best available model
- **Concurrent Operations**: Parallel file processing and API calls
- **Timeout Management**: Prevents hanging operations
- **Memory Optimization**: Efficient memory usage for large projects

## 🛠️ Installation & Setup

### Local Development
```bash
pip install -r requirements.txt
python autonomydz_improved.py
```

### RunPod Deployment
1. Upload the project files to your RunPod instance
2. Run the setup script:
```bash
chmod +x setup_runpod.sh
./setup_runpod.sh
```
3. Start the agent:
```bash
python autonomydz_improved.py
```

## 📋 System Requirements

### Minimum Requirements
- **GPU**: 16GB VRAM (for qwen2.5-coder:14b)
- **CPU**: 4+ cores
- **RAM**: 8GB
- **Storage**: 20GB free space

### Recommended for Best Performance
- **GPU**: 24GB+ VRAM (for qwen2.5-coder:32b)
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 50GB+ SSD

## 🎯 Supported Project Types

- **Next.js**: Full-stack React framework with SSR
- **React**: Modern React applications with hooks
- **Vite**: Fast build tool for modern web development
- **Express**: Node.js backend applications
- **FastAPI**: Modern Python web framework
- **Flask**: Lightweight Python web framework
- **Vanilla**: Plain HTML/CSS/JS projects

## 🔧 Key Features

### Intelligent Code Generation
- Context-aware code generation using state-of-the-art LLMs
- Best practices enforcement
- Modern framework patterns
- TypeScript support

### Real-time Development
- Live development server integration
- Hot reload support
- Automatic dependency installation
- Build process automation

### Git Integration
- Automatic repository initialization
- Commit message generation
- Remote repository setup
- Branch management

### RunPod Cloud Features
- Container-optimized resource usage
- Automatic model selection based on GPU
- Persistent storage integration
- Scalable deployment options

## 📱 Usage Examples

### Creating a Next.js Project
```python
# The agent will guide you through:
# 1. Project configuration
# 2. Feature selection
# 3. Code generation
# 4. Dependency installation
# 5. Git setup
# 6. Development server launch
```

### Adding Features
```bash
# Interactive commands:
feature  # Add new functionality
fix      # Fix bugs or issues
explain  # Code explanation
deploy   # RunPod deployment guide
status   # Project status overview
```

## 🧠 Model Configuration

The agent automatically selects the best available model based on your GPU:

- **48GB+ VRAM**: qwen2.5-coder:32b (best quality)
- **24GB VRAM**: qwen2.5-coder:14b (recommended)
- **16GB VRAM**: deepseek-coder:6.7b (minimum)

## 🚀 RunPod Deployment Best Practices

### Container Setup
1. Use the official Ollama Docker image as base
2. Install Node.js and Python dependencies
3. Configure environment variables
4. Set up persistent volumes for projects

### Environment Variables
```bash
OLLAMA_HOST=0.0.0.0:11434
NODE_ENV=development
PORT=3000
```

### Volume Mounts
- `/workspace`: For generated projects
- `/root/.ollama`: For model storage
- `/app/memory`: For persistent agent memory

## 🔍 Troubleshooting

### Common Issues
1. **Model not found**: Run `ollama pull <model-name>`
2. **Port conflicts**: Change the port in project configuration
3. **Memory issues**: Use a smaller model or increase VRAM
4. **Network timeouts**: Increase timeout values in configuration

### Performance Tuning
- Use SSD storage for better I/O performance
- Increase model context length for larger projects
- Enable GPU acceleration for faster inference
- Use model quantization for memory-constrained environments

## 📊 Monitoring & Logging

The agent provides comprehensive logging:
- Model selection and performance metrics
- Resource usage monitoring
- Error tracking and recovery
- Project build status

## 🔄 Updates & Maintenance

Regular updates include:
- New project templates
- Enhanced model support
- Performance optimizations
- Security improvements

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines before submitting pull requests.

## 📞 Support

For RunPod-specific issues:
- Check the RunPod documentation
- Monitor GPU memory usage
- Verify model compatibility
- Review container logs

---

**Made with ❤️ for the RunPod community**
