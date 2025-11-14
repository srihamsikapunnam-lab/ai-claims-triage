#!/usr/bin/env python3
"""
Insurance Claims Backend Server
"""

import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

print("📁 Current directory:", current_dir)
print("📁 Source directory:", src_dir)

# Change to src directory
os.chdir(src_dir)
print("📁 Working directory changed to:", os.getcwd())

try:
    from app import create_app
    print("✅ Successfully imported app from src directory")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📁 Files in src directory:")
    for file in os.listdir(src_dir):
        print(f"   - {file}")
    sys.exit(1)

if __name__ == '__main__':
    app = create_app()
    
    print("🚀 Starting Insurance Claims Backend Server...")
    print("📍 Server URL: http://localhost:5000")
    print("❤️  Health Check: http://localhost:5000/health")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)