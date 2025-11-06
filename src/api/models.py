from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ClaimRequest(BaseModel):
    claim_id: Optional[str] = None
    patient_age: int
    diagnosis: str
    admission_date: str
    discharge_date: str
    claimed_amount: float

class ClaimResponse(BaseModel):
    claim_id: str
    prediction: str
    probability: float
    risk_score: float
    risk_category: str
    explanation: List[str]
    status: str

class ClaimResult(BaseModel):
    claim_id: str
    patient_age: int
    diagnosis: str
    claimed_amount: float
    prediction: str
    risk_category: str
    status: str
    created_at: datetime

class ClaimDetail(BaseModel):
    raw_claim: Dict[str, Any]
    prediction_result: Dict[str, Any]