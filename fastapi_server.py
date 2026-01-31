from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# Create FastAPI app
app = FastAPI(
    title="Insurance Claims Triage API",
    version="2.0",
    description="Medical Insurance Fraud Detection with Authentication & Workflow"
)

# Enable CORS - Must be configured before routes - FIXED FOR PRODUCTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow ALL origins - fixes deployment issue
    allow_credentials=False,  # Changed to False for compatibility with "*"
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize database
from src.api.init_enhanced_db import init_enhanced_database
try:
    init_enhanced_database()
except Exception as e:
    print(f"Database initialization warning: {e}")

# Import and include routers
from src.api.auth.routers import router as auth_router
from src.api.documents.routers import router as documents_router
from src.api.workflows.routers import router as workflows_router
from src.api.batch_routes import router as batch_router
from src.api.chat import router as chat_router

# Register all routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents_router, prefix="/api", tags=["Documents"])
app.include_router(workflows_router, prefix="/api", tags=["Claims & Workflows"])
app.include_router(batch_router, prefix="/api", tags=["Batch Processing"])
app.include_router(chat_router, prefix="", tags=["Chatbot"])

# Mount uploads directory for serving files
if not os.path.exists("uploads"):
    os.makedirs("uploads/documents", exist_ok=True)

# Mount test page
if os.path.exists("test_api.html"):
    from fastapi.responses import FileResponse
    @app.get("/test")
    async def serve_test_page():
        return FileResponse("test_api.html")

# Health check
@app.get("/")
async def root():
    return {
        "message": "Insurance Claims Triage API",
        "version": "2.0",
        "status": "running",
        "features": [
            "JWT Authentication",
            "Document Upload & Management",
            "Claim Workflow Tracking",
            "Company Dashboard",
            "AI Fraud Detection"
        ],
        "endpoints": {
            "auth": "/api/auth/*",
            "claims": "/api/claims/*",
            "documents": "/api/claims/{claim_id}/documents",
            "company": "/api/company/*",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "fastapi", "version": "2.0"}


if __name__ == "__main__":
    print("🚀 Starting FastAPI Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)