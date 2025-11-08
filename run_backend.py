import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.app import app

if __name__ == '__main__':
    import uvicorn; uvicorn.run(app, host="127.0.0.1", port=8000)
