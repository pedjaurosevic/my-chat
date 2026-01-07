import ollama
import os

# Test Kiklop API
os.environ["OLLAMA_HOST"] = "127.0.0.1:11435"

print("Testing Kiklop API (11435)...")
try:
    response = ollama.list()
    print("✅ List models:", [m.name for m in response.models])
except Exception as e:
    print("❌ Error:", e)

# Test Ollama API
os.environ["OLLAMA_HOST"] = "127.0.0.1:11434"

print("\nTesting Ollama API (11434)...")
try:
    response = ollama.list()
    print("✅ List models:", [m.name for m in response.models][:5])
except Exception as e:
    print("❌ Error:", e)
