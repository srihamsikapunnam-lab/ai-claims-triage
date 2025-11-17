from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ClaimStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"

class ClaimStage(str, Enum):
    SUBMISSION = "submission"
    AI_PROCESSING = "ai_processing"
    RISK_ASSESSMENT = "risk_assessment"
    MANUAL_REVIEW = "manual_review"
    FINAL_DECISION = "final_decision"

class ClaimCreate(BaseModel):
    patient_age: int
    diagnosis: str
    admission_date: str
    discharge_date: str
    claimed_amount: float
    description: Optional[str] = None

class ClaimStatusUpdate(BaseModel):
    status: ClaimStatus
    notes: Optional[str] = None

class ClaimResponse(BaseModel):
    id: str
    user_id: int
    status: str
    current_stage: str
    patient_age: int
    diagnosis: str
    claimed_amount: float
    risk_score: Optional[float] = None
    risk_category: Optional[str] = None
    prediction: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClaimDetailResponse(ClaimResponse):
    admission_date: str
    discharge_date: str
    description: Optional[str] = None
    explanation: Optional[List[str]] = None
    lime_explanation: Optional[List[dict]] = None
    full_name: Optional[str] = None
    length_of_stay: Optional[int] = None
    model_version: Optional[str] = None
    status_history: List[dict] = []

class ClaimStatusHistoryResponse(BaseModel):
    id: int
    claim_id: str
    status: str
    notes: Optional[str] = None
    changed_by: int
    changed_by_name: str
    changed_at: datetime

    class Config:
        from_attributes = True

class CompanyDashboardStats(BaseModel):
    total_claims: int
    pending_review: int
    approved: int
    rejected: int
    high_risk: int
    medium_risk: int
    low_risk: int
    avg_processing_time_hours: float
