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

# User Authentication Models - Add this at the bottom of models.py
import hashlib
import secrets
from datetime import datetime

class User:
    def __init__(self, username: str, email: str, password: str, role: str = "user"):
        self.id = None  # Will be set by database
        self.username = username
        self.email = email
        self.password_hash = self.hash_password(password)
        self.role = role
        self.created_at = datetime.now()
        self.is_active = True
    
    def hash_password(self, password: str) -> str:
        """Simple password hashing - SUPER EASY"""
        # Create a salt (random string) for extra security
        salt = "ai_claims_salt_2024"
        # Combine password + salt and hash it
        combined = password + salt
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Check if password matches the hash"""
        # Hash the input password the same way
        salt = "ai_claims_salt_2024"
        combined = password + salt
        input_hash = hashlib.sha256(combined.encode()).hexdigest()
        # Compare with stored hash
        return input_hash == self.password_hash
    
    def to_dict(self):
        """Convert user to dictionary (without password)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }

# Simple in-memory user storage (we'll replace with database later)
users_db = []