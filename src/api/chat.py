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
                SELECT id, diagnosis, claimed_amount, status, risk_score, 
                       created_at, updated_at, risk_category
                FROM claims 
                WHERE id = ?
            """, (claim_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "diagnosis": row[1],
                    "amount": row[2],
                    "status": row[3],
                    "risk_score": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                    "risk_category": row[7]
                }
            
            # Try numeric ID if UUID failed
            try:
                numeric_id = int(claim_id)
                cursor.execute("""
                    SELECT id, diagnosis, claimed_amount, status, risk_score, 
                           created_at, updated_at, risk_category
                    FROM claims 
                    WHERE ROWID = ?
                """, (numeric_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "diagnosis": row[1],
                        "amount": row[2],
                        "status": row[3],
                        "risk_score": row[4],
                        "created_at": row[5],
                        "updated_at": row[6],
                        "risk_category": row[7]
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
    """Processes user messages and returns intent-based responses"""
    
    def __init__(self):
        # Define intent keywords and responses
        self.intents = {
            "greeting": {
                "keywords": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"],
                "responses": [
                    "Hello! I can help with claims processing."
                ]
            },
            "claim_status": {
                "keywords": ["status", "claim status", "check claim", "where is my claim", "tracking"],
                "responses": [
                    "Check your dashboard for your claim status."
                ]
            },
            "fraud": {
                "keywords": ["fraud", "suspicious", "fraud detection"],
                "responses": [
                    "Our AI system detects fraudulent claims and suspicious patterns in claims."
                ]
            },
            "claim_submission": {
                "keywords": ["submit", "new claim", "file claim", "submit claim", "upload", "create claim"],
                "responses": [
                    "Submit claims via the Claims form in the dashboard."
                ]
            },
            "default": {
                "keywords": [],  # Matches everything not above
                "responses": [
                    "I can help with claim submission, claim status, fraud detection, and more. What do you need?"
                ]
            }
        }
    
    def _clean_message(self, message: str) -> str:
        """Normalize message for matching"""
        return message.lower().strip()
    
    def _extract_claim_id(self, message: str) -> Optional[str]:
        """
        Extract claim ID from user message
        
        Patterns supported:
        - CLAIM123, CLAIM-123, Claim123
        - UUID format: 21085f73-883a-4e5d-8f39-1b88972b25fb
        - Numeric: 12345, #12345
        
        Returns:
            Claim ID string or None if not found
        """
        # Pattern 1: CLAIM followed by numbers (CLAIM123, Claim-456)
        match = re.search(r'claim[\s-]*(\d+)', message, re.IGNORECASE)
        if match:
            return f"CLAIM{match.group(1)}"
        
        # Pattern 2: Just numbers with # prefix (#12345, # 12345)
        match = re.search(r'#\s*(\d+)', message)
        if match:
            return match.group(1)
        
        # Pattern 3: UUID format (8-4-4-4-12 hex digits)
        match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', message, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 4: Standalone long numbers that look like IDs
        match = re.search(r'\b(\d{10,})\b', message)
        if match:
            return match.group(1)
        
        return None
    
    def _find_intent(self, message: str) -> tuple:
        """Find the best matching intent for a message"""
        clean_msg = self._clean_message(message)
        
        # Check greeting first (most specific)
        if any(keyword in clean_msg for keyword in self.intents["greeting"]["keywords"]):
            return "greeting", self.intents["greeting"]["responses"]
        
        # Check claim_status
        if any(keyword in clean_msg for keyword in self.intents["claim_status"]["keywords"]):
            return "claim_status", self.intents["claim_status"]["responses"]
        
        # Check fraud
        if any(keyword in clean_msg for keyword in self.intents["fraud"]["keywords"]):
            return "fraud", self.intents["fraud"]["responses"]
        
        # Check claim_submission
        if any(keyword in clean_msg for keyword in self.intents["claim_submission"]["keywords"]):
            return "claim_submission", self.intents["claim_submission"]["responses"]
        
        # Return default if no intent matches
        return "default", self.intents["default"]["responses"]
    
    def process(self, message: str) -> dict:
        """
        Process user message and return intent-based response
        
        First checks if message contains claim ID and fetches claim data from database.
        If claim found, overrides intent to 'claim_status' and returns claim details.
        If claim ID detected but not found, asks user to verify the ID.
        
        Returns:
            {
                "reply": "Response text",
                "intent": "Intent name",
                "claim_id": "Claim ID or null"
            }
        """
        # Try to extract claim ID from message
        claim_id = self._extract_claim_id(message)
        
        if claim_id:
            # Look up claim in database
            claim_data = ClaimDatabase.get_claim(claim_id)
            
            if claim_data:
                # Claim found - return claim details
                reply = self._build_claim_response(claim_data)
                return {
                    "reply": reply,
                    "intent": "claim_status",
                    "claim_id": claim_data['id']
                }
            else:
                # Claim ID mentioned but not found
                reply = f"I couldn't find claim {claim_id} in our system. Could you please verify the claim ID? You can usually find it in your confirmation email or on the dashboard."
                return {
                    "reply": reply,
                    "intent": "claim_status",
                    "claim_id": None
                }
        
        # No claim ID detected - proceed with normal intent matching
        intent_name, responses = self._find_intent(message)
        reply = responses[0]
        
        return {
            "reply": reply,
            "intent": intent_name,
            "claim_id": None
        }
    
    def _build_claim_response(self, claim_data: dict) -> str:
        """
        Build a detailed claim response from database data
        
        Args:
            claim_data: Dictionary with claim information from database
        
        Returns:
            Formatted response string with claim details
        """
        claim_id = claim_data.get('id', 'Unknown')
        status = claim_data.get('status', 'Unknown').replace('_', ' ').title()
        stage = claim_data.get('current_stage', 'Unknown').replace('_', ' ').title()
        risk_category = claim_data.get('risk_category', 'Unknown')
        amount = claim_data.get('amount', 0)
        diagnosis = claim_data.get('diagnosis', 'Not specified')
        
        # Build comprehensive response
        response = f"""📋 **Claim Status: {claim_id}**

✅ **Status:** {status}
📑 **Stage:** {stage}

**Claim Details:**
• Amount Claimed: ${amount:,.2f}
• Risk Category: {risk_category}
• Diagnosis: {diagnosis}
• Patient Age: {claim_data.get('patient_age', 'N/A')}

**Timeline:**
• Admission: {claim_data.get('admission_date', 'N/A')}
• Discharge: {claim_data.get('discharge_date', 'N/A')}

"""
        
        # Add next action based on status and stage
        status_lower = claim_data.get('status', '').lower()
        stage_lower = claim_data.get('current_stage', '').lower()
        
        if status_lower == 'rejected':
            response += "❌ **Next Action:** This claim was rejected. You can appeal by submitting additional documentation to support your case. Contact support for assistance.\n"
        elif status_lower == 'approved':
            response += "✨ **Next Action:** Your claim has been approved! Payment will be processed shortly.\n"
        elif 'under_review' in status_lower or 'processing' in stage_lower:
            response += f"⏳ **Next Action:** Your claim is being reviewed. Current stage: {stage}. We'll notify you once there's an update.\n"
        elif 'missing' in stage_lower or 'document' in stage_lower:
            response += "📎 **Next Action:** We need additional documents to process your claim. Please upload the required files to proceed.\n"
        else:
            response += "❓ **Next Action:** Visit your dashboard for the latest updates on this claim.\n"
        
        return response

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