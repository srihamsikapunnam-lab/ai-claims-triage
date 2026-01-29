#!/usr/bin/env python3
"""
Intent-Based Chatbot API Server
Runs on port 8001 with keyword-based intent recognition and file upload
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import re
import os
from pathlib import Path
import shutil
import sqlite3
from datetime import datetime

# ===== Pydantic Models =====
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None  # Optional model parameter (for compatibility)


class ChatResponse(BaseModel):
    reply: str
    intent: str
    claim_id: Optional[str] = None


class UploadResponse(BaseModel):
    status: str
    filename: str
    message: Optional[str] = None


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
            Claim dict with id, status, risk_category, description, or None if not found
        """
        try:
            conn = sqlite3.connect(ClaimDatabase.DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Try to find by UUID (primary format)
            cursor.execute("""
                SELECT id, status, current_stage, risk_category, risk_score, 
                       description, diagnosis, patient_age, claimed_amount,
                       admission_date, discharge_date
                FROM claims
                WHERE id = ? OR id LIKE ?
                LIMIT 1
            """, (claim_id, f"%{claim_id}%"))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            print(f"[DB ERROR] Claim lookup failed: {str(e)}")
            return None
    
    @staticmethod
    def get_claim_history(claim_id: str, limit: int = 3) -> list:
        """
        Get claim status history
        
        Args:
            claim_id: Claim UUID
            limit: Number of recent entries to retrieve
        
        Returns:
            List of status history entries
        """
        try:
            conn = sqlite3.connect(ClaimDatabase.DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT status, changed_at, notes
                FROM claim_status_history
                WHERE claim_id = ?
                ORDER BY changed_at DESC
                LIMIT ?
            """, (claim_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"[DB ERROR] History lookup failed: {str(e)}")
            return []


# ===== Intent-Based Response Handler =====
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
        amount = claim_data.get('claimed_amount', 0)
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


# ===== FastAPI App Setup =====
app = FastAPI(
    title="Claims Chatbot API",
    version="1.0.0",
    description="Intent-based chatbot for insurance claims processing"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize intent processor
processor = IntentProcessor()


# ===== Endpoints =====
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "Claims Processing Chatbot",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health (GET)",
            "chat": "/chat (POST)",
            "upload": "/upload (POST)",
            "docs": "/docs (SwaggerUI)"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "claims-chatbot"
    }


@app.post("/chat", response_model=ChatResponse)
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


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    """
    File upload endpoint
    
    Upload documents (PDF, JPG, PNG) for claims processing
    
    Args:
        file: UploadFile from multipart/form-data
    
    Returns:
        UploadResponse with status, filename, and message
    
    Raises:
        HTTPException 400: For invalid file type or size
        HTTPException 500: For server errors
    """
    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Validate file type
    allowed_types = {'application/pdf', 'image/jpeg', 'image/png'}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: PDF, JPG, PNG (received: {file.content_type})"
        )
    
    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024  # 5MB
    
    try:
        # Read file content
        contents = await file.read()
        
        if len(contents) > max_size:
            file_size_mb = len(contents) / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds limit. Maximum: 5MB (your file: {file_size_mb:.2f}MB)"
            )
        
        # Sanitize filename (prevent directory traversal)
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Remove any path components
        filename = Path(filename).name
        
        # Save file
        file_path = upload_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        print(f"[UPLOAD] File saved: {filename} ({len(contents)} bytes)")
        
        return UploadResponse(
            status="success",
            filename=filename,
            message=f"✅ File '{filename}' uploaded successfully!"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[UPLOAD] Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )


# ===== Main =====
if __name__ == "__main__":
    print("🚀 Starting Chatbot API Server on http://localhost:8001")
    print("📚 Interactive docs: http://localhost:8001/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
