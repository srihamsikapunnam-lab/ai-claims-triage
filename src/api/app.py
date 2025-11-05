from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI()

# Request model
class ClaimRequest(BaseModel):
    claim_id: Optional[str] = None
    patient_age: int
    diagnosis: str
    admission_date: str
    discharge_date: str
    claimed_amount: float

# Response model  
class ClaimResponse(BaseModel):
    claim_id: str
    prediction: str
    probability: float
    risk_score: float
    risk_category: str
    explanation: List[str]
    status: str

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Medical Insurance Backend API is running"}

# Ping endpoint
@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Backend is running"}

# Predict endpoint
@app.post("/predict", response_model=ClaimResponse)
def predict_claim(claim: ClaimRequest):
    if not claim.claim_id:
        claim.claim_id = str(uuid.uuid4())
    
    return ClaimResponse(
        claim_id=claim.claim_id,
        prediction="Fraud",
        probability=0.82,
        risk_score=0.82,
        risk_category="High",
        explanation=[
            "Claimed amount higher than typical for diagnosis",
            "Length of stay unusually short",
            "Hospital has higher than average previous claims"
        ],
        status="Under Review"
    )