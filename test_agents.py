import requests
import json

# Get token
login_url = "http://localhost:8502/api/auth/login"
login_data = {"pin": "2020"}
resp = requests.post(login_url, json=login_data)
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test agents list
agents_url = "http://localhost:8502/api/agents/available-agents"
resp = requests.get(agents_url, headers=headers)
print("Agents list status:", resp.status_code)
print("Agents list response:", resp.json())

# Test web search (will likely fail without Brave API key)
websearch_url = "http://localhost:8502/api/agents/web-search"
websearch_data = {"query": "test", "num_results": 1}
resp = requests.post(websearch_url, headers=headers, json=websearch_data)
print("Web search status:", resp.status_code)
print("Web search response:", resp.json())
