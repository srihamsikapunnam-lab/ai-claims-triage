from fastapi import APIRouter, HTTPException, Path
from .models import ClaimRequest, ClaimResponse, ClaimResult, ClaimDetail
from .database import save_claim_to_db
from .model_service import process_claim
import uuid
import sqlite3
import json
from typing import List

router = APIRouter()

@router.get("/ping")
def ping():
    return {"status": "ok", "message": "Backend is running"}

@router.post("/predict", response_model=ClaimResponse)
def predict_claim(claim: ClaimRequest):
    try:
        if not claim.claim_id:
            claim.claim_id = str(uuid.uuid4())
        
        prediction_result = model_service.predict(claim.dict())
        prediction_result["claim_id"] = claim.claim_id
        
        save_claim_to_db(claim.dict(), prediction_result)
        
        return ClaimResponse(**prediction_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing claim: {str(e)}")

@router.get("/claims/{claim_id}", response_model=ClaimDetail)
def get_claim_by_id(claim_id: str = Path(..., description="The claim ID")):
    conn = sqlite3.connect('claims.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM claims_raw WHERE claim_id = ?', (claim_id,))
        raw_claim = cursor.fetchone()
        cursor.execute('SELECT * FROM claims_results WHERE claim_id = ?', (claim_id,))
        claim_result = cursor.fetchone()
        
        if not raw_claim or not claim_result:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        columns_raw = [description[0] for description in cursor.description]
        columns_result = [description[0] for description in cursor.description]
        
        raw_dict = dict(zip(columns_raw, raw_claim))
        result_dict = dict(zip(columns_result, claim_result))
        
        if raw_dict.get('raw_json'):
            raw_dict['raw_json'] = json.loads(raw_dict['raw_json'])
        if result_dict.get('explanation'):
            result_dict['explanation'] = json.loads(result_dict['explanation'])
        
        return ClaimDetail(
            raw_claim=raw_dict,
            prediction_result=result_dict
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@router.get("/claims/", response_model=List[ClaimResult])
def get_all_claims(limit: int = 10):
    conn = sqlite3.connect('claims.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT r.claim_id, r.patient_age, r.diagnosis, r.claimed_amount, 
                   res.prediction, res.risk_category, res.status, res.created_at
            FROM claims_raw r
            JOIN claims_results res ON r.claim_id = res.claim_id
            ORDER BY res.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        claims = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        result = []
        for claim in claims:
            claim_dict = dict(zip(columns, claim))
            result.append(ClaimResult(**claim_dict))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()