from fastapi import FastAPI
from routes import router
from database import init_database

app = FastAPI(title="AI Claims Triage API", version="1.0.0")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "AI Claims Triage Backend API - Week 2"}

@app.on_event("startup")
def startup_event():
    init_database()