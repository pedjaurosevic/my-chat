import requests
import json

# Test Kiklop API directly
response = requests.get("http://127.0.0.1:11435/api/tags")
print("Kiklop API response:")
print(json.dumps(response.json(), indent=2))

# Test Ollama
response2 = requests.get("http://127.0.0.1:11434/api/tags")
data2 = response2.json()
print(f"\nOllama models: {[m['name'] for m in data2['models'][:5]]}")
