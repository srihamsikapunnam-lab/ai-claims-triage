from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="AI Claims Triage")

app.include_router(router)
