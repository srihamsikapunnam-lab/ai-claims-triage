import sys
import os

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from api.app import app

if __name__ == '__main__':
    import uvicorn
    print("🚀 Starting Backend Server from src/api/app.py")
    print("🌐 Server: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)