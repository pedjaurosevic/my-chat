"""
OLLAMA.CORE FastAPI Main Application
Minimal version for testing
"""

from fastapi import FastAPI

# Create minimal FastAPI app
app = FastAPI(title="OLLAMA.CORE", version="1.0.0", description="AI Chat application")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OLLAMA.CORE", "version": "1.0.0"}


@app.post("/api/chat")
async def simple_chat(request: dict):
    """Chat endpoint with real Ollama models"""
    import ollama
    import time

    message = request.get("message", "")
    model = request.get("model", "llama3.2:3b")

    if not message:
        return {
            "response": "Error: No message provided",
            "model": model,
            "source": "Ollama (11434)",
            "cached": False,
            "enhanced": False,
            "processing_time": 0.0,
        }

    start_time = time.time()

    try:
        # Get response from Ollama
        response = ollama.chat(
            model=model, messages=[{"role": "user", "content": message}]
        )

        full_response = response["message"]["content"]
        processing_time = time.time() - start_time

        return {
            "response": full_response,
            "model": model,
            "source": "Ollama (11434)",
            "cached": False,
            "enhanced": False,
            "processing_time": round(processing_time, 2),
        }

    except Exception as e:
        processing_time = time.time() - start_time
        return {
            "response": f"Error: {str(e)}",
            "model": model,
            "source": "Ollama (11434)",
            "cached": False,
            "enhanced": False,
            "processing_time": round(processing_time, 2),
        }
