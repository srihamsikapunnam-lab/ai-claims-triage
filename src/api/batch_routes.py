from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional
import time

router = APIRouter()

# UPDATED Request model - accepts both fields
class BatchRequest(BaseModel):
    claims_data: Optional[List[Dict[str, Any]]] = None
    claims: Optional[List[Dict[str, Any]]] = None
    
    @validator('claims', always=True)
    def validate_claims(cls, v, values):
        """
        If 'claims' field is provided, use it.
        Otherwise fall back to 'claims_data'
        """
        if v is not None:
            return v
        return values.get('claims_data')

# Response model (unchanged)
class BatchResponse(BaseModel):
    status: str
    message: str
    processed: int
    results: List[Dict[str, Any]]

@router.post("/batch/predict", response_model=BatchResponse)
async def batch_predict(request: BatchRequest):
    """Process multiple claims in batch - FASTAPI VERSION"""
    try:
        # UPDATED: Get data from either field
        claims_data = request.claims  # This will contain data from either 'claims' or 'claims_data'
        
        if not claims_data:
            raise HTTPException(status_code=400, detail="No claims data provided. Use either 'claims' or 'claims_data' field.")
        
        if len(claims_data) > 100:
            raise HTTPException(status_code=400, detail="Too many claims. Maximum 100 per batch.")
        
        print(f"🔄 Processing batch of {len(claims_data)} claims...")
        print(f"📦 Field used: {'claims' if request.claims else 'claims_data'}")
        
        results = []
        for i, claim in enumerate(claims_data):
            # Simple risk calculation
            risk_score = 0.3 + (i * 0.1) % 0.7
            
            result = {
                "claim_id": claim.get("claim_id", f"batch_{i}"),
                "risk_score": round(risk_score, 2),
                "risk_category": "High" if risk_score > 0.7 else "Medium" if risk_score > 0.4 else "Low",
                "status": "processed"
            }
            results.append(result)
        
        # Simulate processing time
        time.sleep(1)
        
        print(f"✅ Batch processing complete! Processed {len(results)} claims.")
        
        return BatchResponse(
            status="success",
            message=f"Batch processing completed for {len(claims_data)} claims",
            processed=len(results),
            results=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

# The rest of your code remains the same...
@router.get("/batch/status")
async def batch_status():
    """Get batch processing system status"""
    return {
        "status": "active",
        "service": "batch_processing",
        "max_batch_size": 100,
        "features": ["multiple_claims", "bulk_predictions", "summary_analytics"],
        "version": "1.0"
    }

print("✅ FastAPI Batch routes loaded!")