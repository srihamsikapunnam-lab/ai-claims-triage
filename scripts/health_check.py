from fastapi.testclient import TestClient
import json
import sys
import os

# Ensure repo root is on path so we can import fastapi_server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fastapi_server

client = TestClient(fastapi_server.app)
resp = client.get('/')
print('STATUS_CODE:', resp.status_code)
try:
    print(json.dumps(resp.json(), indent=2))
except Exception as e:
    print('Failed to parse JSON response:', e)
    print(resp.text)
