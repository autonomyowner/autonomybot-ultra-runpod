# Use official Python runtime as base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY autonomydz_improved.py .
COPY setup_runpod.sh .

# Create directories for persistence
RUN mkdir -p /workspace /app/memory

# Make scripts executable
RUN chmod +x setup_runpod.sh

# Expose ports
EXPOSE 11434 3000 8080

# Environment variables
ENV OLLAMA_HOST=0.0.0.0:11434
ENV PYTHONPATH=/app
ENV WORKSPACE_DIR=/workspace

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:11434/api/tags || exit 1

# Start script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
