"""
FastAPI Chatbot Server for Claims Processing
Simple rule-based chatbot with CORS support
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Claims Chatbot", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

# Rule-based chatbot logic
def get_chatbot_response(message: str) -> str:
    """
    Generate a response based on the user's message.
    Uses simple rule-based matching for common queries.
    """
    message_lower = message.lower().strip()
    
    # Greeting patterns
    greeting_keywords = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
    if any(keyword in message_lower for keyword in greeting_keywords):
        return "Hello! I can help with claims processing."
    
    # Claim status patterns
    status_keywords = ["status", "claim status", "where is my claim", "track my claim", "claim progress"]
    if any(keyword in message_lower for keyword in status_keywords):
        return "Check your dashboard for claim status."
    
    # Fraud detection patterns
    fraud_keywords = ["fraud", "suspicious", "fraud detection", "security", "detect fraud"]
    if any(keyword in message_lower for keyword in fraud_keywords):
        return "Our AI system detects suspicious patterns."
    
    # Claim submission patterns
    submission_keywords = ["submit", "claim submission", "new claim", "file a claim", "submit claim"]
    if any(keyword in message_lower for keyword in submission_keywords):
        return "Submit claims via the 'New Claim' form."
    
    # Default response
    return "I can help with claims-related questions."

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "claims-chatbot"}

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    Accepts a message and returns a chatbot response
    """
    reply = get_chatbot_response(request.message)
    return ChatResponse(reply=reply)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Claims Processing Chatbot",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
