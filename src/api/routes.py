from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.model_service import model_service
import uuid
import sqlite3

router = APIRouter()


# --------------------
# Pydantic Schemas
# --------------------
class ClaimRequest(BaseModel):
    claim_id: str | None = None
    patient_age: int
    claimed_amount: float
    length_of_stay: int
    gender: str | None = None
    diagnosis: str | None = None


class ClaimResponse(BaseModel):
    claim_id: str
    prediction: str
    probability: float
    risk_score: int
    risk_category: str
    explanation: list
    status: str
    status_label: str | None = None
    model_version: str | None = None


# --------------------
# Routes
# --------------------
@router.post("/predict", response_model=ClaimResponse)
async def predict_claim(claim: ClaimRequest):
    try:
        if not claim.claim_id:
            claim.claim_id = str(uuid.uuid4())

        prediction_result = model_service.predict(claim.dict())
        prediction_result["claim_id"] = claim.claim_id

        # Save to DB
        conn = sqlite3.connect("claims.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO claims_raw (claim_id, raw_json)
            VALUES (?, ?)
        """, (claim.claim_id, str(claim.dict())))

        cursor.execute("""
            INSERT OR REPLACE INTO claims_results
            (claim_id, prediction, probability, risk_score, risk_category, explanation, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            claim.claim_id,
            prediction_result.get("prediction"),
            prediction_result.get("probability"),
            prediction_result.get("risk_score"),
            prediction_result.get("risk_category"),
            str(prediction_result.get("explanation")),
            prediction_result.get("status"),
        ))

        conn.commit()
        conn.close()

        return ClaimResponse(**prediction_result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ping")
async def ping():
    return {"status": "ok"}


@router.get("/health")
async def health():
    return {"status": "healthy"}
