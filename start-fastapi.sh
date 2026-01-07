#!/bin/bash
cd /home/peterofovik/my-chat
source venv/bin/activate

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Warning: Ollama server may not be running on port 11434"
    echo "Starting Ollama.CORE anyway..."
fi

# Check if port 8501 is already in use
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo "Port 8501 is already in use. Trying to kill existing process..."
    fuser -k 8501/tcp
    sleep 2
fi

echo "Starting OLLAMA.CORE FastAPI server on port 8501..."
echo "Access at: http://localhost:8501"
echo "Public URL: https://moj.perasper.com"

# Run FastAPI with uvicorn
exec python3 -m uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8501 --reload