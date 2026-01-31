from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import re
import sqlite3
from datetime import datetime

router = APIRouter()

# ===== Pydantic Models =====
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None  # Optional model parameter (for compatibility)

class ChatResponse(BaseModel):
    reply: str
    intent: str
    claim_id: Optional[str] = None

# ===== Database Helper =====
class ClaimDatabase:
    """Database helper for claim lookups"""
    
    DB_PATH = "claims.db"
    
    @staticmethod
    def get_claim(claim_id: str) -> Optional[dict]:
        """
        Retrieve claim details from database by ID (UUID or numeric)
        
        Args:
            claim_id: UUID string or numeric ID
        
        Returns:
            dict with claim data or None if not found
        """
        try:
            conn = sqlite3.connect(ClaimDatabase.DB_PATH)
            cursor = conn.cursor()
            
            # Try UUID first (more specific)
            cursor.execute("""
                SELECT id, patient_name, diagnosis, amount, status, risk_score, 
                       created_at, updated_at, risk_category
                FROM claims 
                WHERE id = ?
            """, (claim_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "patient_name": row[1],
                    "diagnosis": row[2],
                    "amount": row[3],
                    "status": row[4],
                    "risk_score": row[5],
                    "created_at": row[6],
                    "updated_at": row[7],
                    "risk_category": row[8]
                }
            
            # Try numeric ID if UUID failed
            try:
                numeric_id = int(claim_id)
                cursor.execute("""
                    SELECT id, patient_name, diagnosis, amount, status, risk_score, 
                           created_at, updated_at, risk_category
                    FROM claims 
                    WHERE ROWID = ?
                """, (numeric_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "patient_name": row[1],
                        "diagnosis": row[2],
                        "amount": row[3],
                        "status": row[4],
                        "risk_score": row[5],
                        "created_at": row[6],
                        "updated_at": row[7],
                        "risk_category": row[8]
                    }
            except ValueError:
                pass  # Not a numeric ID
            
            return None
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

# ===== Intent Processor =====
class IntentProcessor:
    """Process user messages and classify intent with claim awareness"""
    
    def __init__(self):
        # Intent patterns with claim-aware responses
        self.intents = {
            "claim_status": {
                "patterns": [
                    r"status.*claim", r"claim.*status", r"where.*claim",
                    r"check.*claim", r"claim.*check", r"track.*claim",
                    r"find.*claim", r"claim.*find"
                ],
                "response": "I can help you check your claim status. Please provide your claim ID.",
                "requires_claim": True
            },
            "claim_submission": {
                "patterns": [
                    r"submit.*claim", r"new.*claim", r"file.*claim",
                    r"create.*claim", r"start.*claim", r"how.*submit"
                ],
                "response": "To submit a new claim, please fill out the claim form with your patient information, diagnosis, and supporting documents.",
                "requires_claim": False
            },
            "rejection_help": {
                "patterns": [
                    r"reject.*claim", r"claim.*reject", r"denied.*claim",
                    r"why.*reject", r"appeal.*claim", r"claim.*appeal"
                ],
                "response": "If your claim was rejected, you can appeal within 30 days by providing additional documentation or correcting the information.",
                "requires_claim": False
            },
            "document_help": {
                "patterns": [
                    r"upload.*document", r"document.*upload", r"attach.*file",
                    r"add.*document", r"missing.*document", r"document.*missing"
                ],
                "response": "You can upload supporting documents like medical reports, bills, and prescriptions when submitting your claim.",
                "requires_claim": False
            },
            "general_help": {
                "patterns": [
                    r"help", r"what.*do", r"how.*work", r"support",
                    r"assist", r"guide"
                ],
                "response": "I can help with claim submission, checking claim status, understanding rejections, and document uploads. What would you like to know?",
                "requires_claim": False
            }
        }
    
    def extract_claim_id(self, message: str) -> Optional[str]:
        """Extract claim ID from message using regex patterns"""
        # UUID pattern
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        uuid_match = re.search(uuid_pattern, message, re.IGNORECASE)
        if uuid_match:
            return uuid_match.group(0)
        
        # Numeric ID pattern (simple numbers)
        numeric_pattern = r'\b\d{1,10}\b'
        numeric_matches = re.findall(numeric_pattern, message)
        if numeric_matches:
            # Return the last numeric match (most likely the claim ID)
            return numeric_matches[-1]
        
        return None
    
    def classify_intent(self, message: str) -> str:
        """Classify the intent of the message"""
        message_lower = message.lower()
        
        for intent, data in self.intents.items():
            for pattern in data["patterns"]:
                if re.search(pattern, message_lower):
                    return intent
        
        return "general"
    
    def process(self, message: str) -> dict:
        """Process message and return response with intent and claim data"""
        intent = self.classify_intent(message)
        claim_id = self.extract_claim_id(message)
        
        # Get base response
        if intent in self.intents:
            response = self.intents[intent]["response"]
            requires_claim = self.intents[intent]["requires_claim"]
        else:
            response = "I'm here to help with your insurance claims. You can ask about claim status, submission, rejections, or document uploads."
            requires_claim = False
        
        # If intent requires claim and we have one, fetch claim data
        if requires_claim and claim_id:
            claim_data = ClaimDatabase.get_claim(claim_id)
            if claim_data:
                response = f"Found your claim. Status: {claim_data['status']}, Amount: ${claim_data['amount']:.2f}, Risk Score: {claim_data['risk_score']:.2f}"
            else:
                response = f"I couldn't find a claim with ID '{claim_id}'. Please check your claim ID and try again."
        
        # If no claim ID but intent requires one
        elif requires_claim and not claim_id:
            response = "To check your claim status, please provide your claim ID (it looks like a long number or UUID)."
        
        return {
            "reply": response,
            "intent": intent,
            "claim_id": claim_id
        }

# Initialize processor
processor = IntentProcessor()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint - NOW WITH CLAIM AWARENESS
    
    Process user message and return intent-based response with intent classification.
    Automatically detects claim IDs and fetches claim data from database.
    
    Args:
        request: ChatRequest with "message" field
    
    Returns:
        ChatResponse with "reply", "intent", and optional "claim_id" fields
    
    Raises:
        HTTPException 400: For empty or invalid messages
    """
    # Process the message - handle empty message as default response
    if not request.message or not request.message.strip():
        # Return default response for empty message
        result = {
            "reply": "I can help with claim submission, claim status, rejections, and document management. What would you like to know?",
            "intent": "default",
            "claim_id": None
        }
    else:
        # Process the message (now with claim awareness)
        result = processor.process(request.message)
    
    print(f"[CHAT] Intent: {result['intent']}, Claim ID: {result.get('claim_id', 'None')}")
    
    return ChatResponse(
        reply=result["reply"],
        intent=result["intent"],
        claim_id=result.get("claim_id")
    )