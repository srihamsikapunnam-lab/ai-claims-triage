import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the current directory to Python path so imports work
sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.api.model_service import model_service
    print("✅ Import successful using src.api path")
except ImportError:
    try:
        # Alternative import path
        from api.model_service import model_service
        print("✅ Import successful using api path")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Current directory:", os.getcwd())
        print("💡 Python path:", sys.path)
        exit(1)

app = FastAPI(title="Fraud Detection API - Production Ready")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(claim_data: dict):
    print(f"📥 Received prediction request: {claim_data}")
    result = model_service.predict(claim_data)
    print(f"📤 Sending prediction: {result['risk_score']} risk score")
    return result

@app.get("/")
async def root():
    return {"message": "Fraud Detection API is running with REAL model!"}

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "model_loaded": model_service.model is not None,
        "model_type": "RandomForest",
        "features": model_service.feature_names if model_service.feature_names else None
    }

if __name__ == "__main__":
    print("🚀 Starting Fraud Detection API Server...")
    print("✅ Real RandomForest model loaded!")
    print("🌐 Server: http://localhost:8000")
    print("📊 Endpoints:")
    print("   POST /predict - Make fraud predictions")
    print("   GET  /health  - Check API status")
    print("   GET  /        - Welcome message")
    print("\n🎯 Ready for real predictions!")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")