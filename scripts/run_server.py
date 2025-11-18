import sys
from pathlib import Path
import uvicorn

# Ensure repo root is on sys.path so `src` imports resolve when run from other CWDs
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

try:
    import fastapi_server
except Exception as e:
    print('Failed to import fastapi_server:', e)
    raise

if __name__ == '__main__':
    print('Starting uvicorn with app from fastapi_server...')
    uvicorn.run(fastapi_server.app, host='0.0.0.0', port=8000)
