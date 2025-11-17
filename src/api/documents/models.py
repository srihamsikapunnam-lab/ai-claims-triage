from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    MEDICAL_REPORT = "medical_report"
    BILL = "bill"
    PRESCRIPTION = "prescription"
    ID_PROOF = "id_proof"
    INSURANCE_CARD = "insurance_card"
    OTHER = "other"

class DocumentUpload(BaseModel):
    document_type: DocumentType
    description: Optional[str] = None

class DocumentResponse(BaseModel):
    id: int
    claim_id: str
    filename: str
    document_type: str
    file_size: int
    uploaded_at: datetime
    uploaded_by: int
    description: Optional[str] = None

    class Config:
        from_attributes = True
