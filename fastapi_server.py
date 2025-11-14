from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(title="Insurance Claims API", version="1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from src.api.batch_routes import router as batch_router
app.include_router(batch_router, prefix="/api")

# Health check
@app.get("/")
async def root():
    return {
        "message": "Insurance Claims API - FastAPI",
        "status": "running",
        "endpoints": {
            "batch_status": "/api/batch/status",
            "batch_predict": "/api/batch/predict"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "fastapi"}

if __name__ == "__main__":
    print("🚀 Starting FastAPI Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)