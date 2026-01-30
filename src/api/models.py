from pydantic import BaseModel
from typing import Optional, List, Any


class ClaimRequest(BaseModel):
    claim_id: Optional[str] = None
    patient_age: Optional[int] = None
    gender: Optional[str] = None
    diagnosis: Optional[str] = None
    claimed_amount: Optional[float] = None
    length_of_stay: Optional[int] = None


class ClaimResponse(BaseModel):
    claim_id: str
    prediction: str
    probability: float
    risk_score: int
    risk_category: str
    explanation: List[Any]
    status: str
    status_label: Optional[str] = None
    model_version: Optional[str] = None
