from fastapi import FastAPI
from .routes import router
from .database import init_database
import uvicorn

app = FastAPI(title="AI Claims Triage API", version="1.0.0")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "AI Claims Triage Backend API - Week 2"}

@app.on_event("startup")
def startup_event():
    init_database()
    print("✅ Database initialized")

# Add this to actually run the server
if __name__ == "__main__":
    print("🚀 Starting AI Claims Triage API Server...")
    print("🌐 Server running on: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")