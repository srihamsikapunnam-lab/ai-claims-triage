from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ensure repo root is on sys.path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

import fastapi_server

client = TestClient(fastapi_server.app)
# Authenticate as demo admin to call company endpoints
login = client.post('/api/auth/login', json={'email': 'admin@demo.com', 'password': 'admin123'})
token = None
if login.status_code == 200:
    token = login.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
else:
    print('Admin login failed', login.status_code, login.text)
    headers = {}

for path in ['/api/company/dashboard/approval-rate','/api/company/dashboard/total-value','/api/company/dashboard/avg-processing-time']:
    resp = client.get(path, headers=headers)
    print(path, resp.status_code, resp.json())
