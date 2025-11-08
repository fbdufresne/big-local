#!/bin/bash

# Local BigMotion Startup Script

echo "🎬 Starting Local BigMotion..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create output directories if they don't exist
mkdir -p output temp

# Start services
echo "📦 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Wait for Ollama to be ready
echo "🤖 Waiting for Ollama to be ready (this may take a few minutes on first run)..."
until docker-compose exec -T ollama ollama list > /dev/null 2>&1; do
    echo "   Still waiting for Ollama..."
    sleep 5
done

# Check if llama3.2 model is available
if ! docker-compose exec -T ollama ollama list | grep -q "llama3.2"; then
    echo "📥 Downloading Llama 3.2 model (first time only, ~2GB)..."
    docker-compose exec -T ollama ollama pull llama3.2
fi

echo ""
echo "✅ Local BigMotion is ready!"
echo ""
echo "🌐 Web Interface: http://localhost:5000"
echo "🔧 API Endpoint:  http://localhost:5000/api"
echo ""
echo "📊 View logs with: docker-compose logs -f"
echo "🛑 Stop with:      docker-compose down"
echo ""
