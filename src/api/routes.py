from fastapi import APIRouter, HTTPException, Path
from .models import ClaimRequest, ClaimResponse, ClaimResult, ClaimDetail
from .database import save_claim_to_db
from .model_service import model_service
import uuid
import sqlite3
import json
from typing import List

router = APIRouter()

@router.get('/ping')
def ping():
    return {'status': 'ok', 'message': 'Backend is running'}

@router.get('/health')
async def health_check():
    return {'status': 'healthy', 'message': 'Backend connected'}

@router.post('/predict', response_model=ClaimResponse)
def predict_claim(claim: ClaimRequest):
    try:
        if not claim.claim_id:
            claim.claim_id = str(uuid.uuid4())
        
        prediction_result = model_service.predict(claim.dict())
        prediction_result['claim_id'] = claim.claim_id
        
        save_claim_to_db(claim.dict(), prediction_result)
        
        return ClaimResponse(**prediction_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error processing claim: {str(e)}')
