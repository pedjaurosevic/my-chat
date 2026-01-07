import requests
import json

# Get token
login_url = "http://localhost:8502/api/auth/login"
login_data = {"pin": "2020"}
resp = requests.post(login_url, json=login_data)
print("Login status:", resp.status_code)
print("Login response:", resp.json())
token = resp.json()["access_token"]
print("Token:", token[:20] + "...")

# Test endpoint with token
headers = {"Authorization": f"Bearer {token}"}
models_url = "http://localhost:8502/api/chat/models"
resp2 = requests.get(models_url, headers=headers)
print("Models status:", resp2.status_code)
print("Models response:", resp2.json())

# Test without token
resp3 = requests.get(models_url)
print("Models without auth status:", resp3.status_code)
print("Models without auth response:", resp3.text)
