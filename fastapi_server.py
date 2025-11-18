from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import easyocr
import sqlite3
from datetime import datetime
import numpy as np
from PIL import Image
import io
from thefuzz import fuzz

# Initialize EasyOCR Reader (lazy loading to avoid startup delay)
reader = None

def get_ocr_reader():
    """Lazy load EasyOCR Reader on first use"""
    global reader
    if reader is None:
        print("🔍 Initializing EasyOCR Reader...")
        reader = easyocr.Reader(['en'], gpu=False)
        print("✅ EasyOCR Reader initialized")
    return reader

# Create FastAPI app
app = FastAPI(
    title="Insurance Claims Triage API",
    version="2.0",
    description="Medical Insurance Fraud Detection with Authentication & Workflow"
)

# Enable CORS - Must be configured before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "https://ai-claims.netlify.app",  # Production frontend
        "https://*.netlify.app",  # Netlify preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize database
from src.api.init_enhanced_db import init_enhanced_database
try:
    init_enhanced_database()
except Exception as e:
    print(f"Database initialization warning: {e}")

# Initialize training_data_verified table
def init_verification_table():
    """Create training_data_verified table if it doesn't exist"""
    try:
        conn = sqlite3.connect('claims.db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_data_verified (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                extraction_score REAL,
                extracted_text TEXT
            )
        """)
        conn.commit()
        conn.close()
        print("✅ training_data_verified table initialized")
    except Exception as e:
        print(f"Warning: Could not initialize verification table: {e}")

init_verification_table()

# Import and include routers
from src.api.auth.routers import router as auth_router
from src.api.documents.routers import router as documents_router
from src.api.workflows.routers import router as workflows_router
from src.api.batch_routes import router as batch_router

# Register all routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents_router, prefix="/api", tags=["Documents"])
app.include_router(workflows_router, prefix="/api", tags=["Claims & Workflows"])
app.include_router(batch_router, prefix="/api", tags=["Batch Processing"])

# Mount uploads directory for serving files
if not os.path.exists("uploads"):
    os.makedirs("uploads/documents", exist_ok=True)

# Mount test page
if os.path.exists("test_api.html"):
    from fastapi.responses import FileResponse
    @app.get("/test")
    async def serve_test_page():
        return FileResponse("test_api.html")

# Health check
@app.get("/")
async def root():
    return {
        "message": "Insurance Claims Triage API",
        "version": "2.0",
        "status": "running",
        "features": [
            "JWT Authentication",
            "Document Upload & Management",
            "Claim Workflow Tracking",
            "Company Dashboard",
            "AI Fraud Detection"
        ],
        "endpoints": {
            "auth": "/api/auth/*",
            "claims": "/api/claims/*",
            "documents": "/api/claims/{claim_id}/documents",
            "company": "/api/company/*",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "fastapi", "version": "2.0"}


# OCR Verification Endpoint
@app.post("/api/verify-claim-document")
async def verify_claim_document(
    file: UploadFile = File(...),
    patient_name: str = Form(...),
    amount: str = Form(...),
    date: str = Form(...)
):
    """
    Verify claim document using OCR and fuzzy matching.
    Returns verification status and confidence scores.
    """
    try:
        # Read uploaded image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to numpy array for EasyOCR
        image_np = np.array(image)
        
        # Perform OCR
        print(f"🔍 Running OCR on {file.filename}...")
        ocr_reader = get_ocr_reader()
        ocr_results = ocr_reader.readtext(image_np)
        
        # Extract all text from OCR results
        extracted_text = " ".join([text for _, text, _ in ocr_results])
        print(f"📄 Extracted text: {extracted_text[:200]}...")
        
        # Fuzzy match patient name
        name_scores = [fuzz.partial_ratio(patient_name.lower(), text.lower()) 
                      for _, text, _ in ocr_results]
        best_name_score = max(name_scores) if name_scores else 0
        
        # Check if amount exists in extracted text
        amount_clean = amount.replace('$', '').replace(',', '').replace('₹', '').strip()
        amount_found = any(amount_clean in text.replace(',', '').replace('$', '').replace('₹', '') 
                          for _, text, _ in ocr_results)
        
        # Calculate overall verification score
        name_verified = best_name_score > 80
        amount_score = 100 if amount_found else 0
        overall_score = (best_name_score + amount_score) / 2
        
        # Determine if verified
        is_verified = name_verified and amount_found
        
        # If verified, store in database
        if is_verified:
            conn = sqlite3.connect('claims.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO training_data_verified 
                (patient_name, amount, date, extraction_score, extracted_text)
                VALUES (?, ?, ?, ?, ?)
            """, (patient_name, float(amount_clean), date, overall_score, extracted_text))
            conn.commit()
            record_id = cursor.lastrowid
            conn.close()
            
            return {
                "verified": True,
                "record_id": record_id,
                "scores": {
                    "name_match": best_name_score,
                    "amount_found": amount_found,
                    "overall": overall_score
                },
                "extracted_text": extracted_text,
                "message": "Document verified successfully and saved to training data"
            }
        else:
            # Return failure with details
            return {
                "verified": False,
                "scores": {
                    "name_match": best_name_score,
                    "amount_found": amount_found,
                    "overall": overall_score
                },
                "extracted_text": extracted_text,
                "message": f"Verification failed. Name match: {best_name_score}%, Amount found: {amount_found}"
            }
            
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")


@app.post("/api/submit-verified-claim")
async def submit_verified_claim(
    file: UploadFile = File(...),
    patient_name: str = Form(...),
    patient_age: str = Form(...),
    diagnosis: str = Form(...),
    amount: str = Form(...),
    admission_date: str = Form(...),
    discharge_date: str = Form(...)
):
    """
    Submit a new claim with automatic OCR verification and ML fraud detection.
    Pipeline: OCR Verification -> Duration Calculation -> ML Model -> Save to DB
    Supports Image (JPG/PNG), PDF, and TXT files.
    """
    import uuid
    import pypdf
    from datetime import datetime
    
    try:
        # Read file content
        contents = await file.read()
        extracted_text = ""
        
        # ========== STEP A: OCR VERIFICATION ==========
        # Extract text based on file type
        file_extension = file.filename.lower().split('.')[-1]
        
        if file_extension in ['jpg', 'jpeg', 'png']:
            # Image file - Use EasyOCR
            print(f"🖼️ Processing image file: {file.filename}")
            image = Image.open(io.BytesIO(contents))
            image_np = np.array(image)
            ocr_reader = get_ocr_reader()
            ocr_results = ocr_reader.readtext(image_np)
            extracted_text = " ".join([text for _, text, _ in ocr_results])
            
        elif file_extension == 'pdf':
            # PDF file - Use pypdf
            print(f"📄 Processing PDF file: {file.filename}")
            pdf_file = io.BytesIO(contents)
            pdf_reader = pypdf.PdfReader(pdf_file)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + " "
                
        elif file_extension == 'txt':
            # Text file - Direct read
            print(f"📝 Processing text file: {file.filename}")
            extracted_text = contents.decode('utf-8')
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}. Please use JPG, PNG, PDF, or TXT.")
        
        print(f"📄 Extracted text: {extracted_text[:200]}...")
        
        # Verify patient_name using fuzzy matching (>80% threshold)
        name_score = fuzz.partial_ratio(patient_name.lower(), extracted_text.lower())
        name_verified = name_score > 80
        
        # Verify amount exists in extracted text
        amount_clean = amount.replace('$', '').replace(',', '').replace('₹', '').strip()
        amount_found = amount_clean in extracted_text.replace(',', '').replace('$', '').replace('₹', '')
        
        # Calculate verification score
        overall_score = (name_score + (100 if amount_found else 0)) / 2
        
        # Check if OCR verification passed
        if not name_verified or not amount_found:
            # Verification FAILED - Return immediately
            snippet = extracted_text[:300] + "..." if len(extracted_text) > 300 else extracted_text
            return {
                "success": False,
                "message": f"Mismatch detected. OCR read: {snippet}",
                "verification": {
                    "name_match": name_score,
                    "amount_found": amount_found,
                    "overall_score": overall_score
                }
            }
        
        print(f"✅ OCR Verification passed (Name: {name_score}%, Amount: {amount_found})")
        
        # ========== STEP B: CALCULATE DURATION & ML FRAUD CHECK ==========
        # Parse dates
        try:
            admit_dt = datetime.strptime(admission_date, '%Y-%m-%d')
            discharge_dt = datetime.strptime(discharge_date, '%Y-%m-%d')
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
        
        # Calculate duration (at least 1 day)
        duration = max((discharge_dt - admit_dt).days, 1)
        print(f"📅 Duration of stay: {duration} days")
        
        # Load ML model and make prediction
        from src.api.model_service import FraudModelService
        model_service = FraudModelService()
        
        # Prepare data for ML model (matching exact feature order)
        claim_data = {
            'patient_age': int(patient_age),
            'claimed_amount': float(amount_clean),
            'length_of_stay': duration,
            'diagnosis': diagnosis,
            'gender': 'Unknown'  # Default - can be added to form later
        }
        
        # Run fraud prediction
        prediction_result = model_service.predict(claim_data)
        
        # Extract fraud probability (0.0-1.0 scale) - represents probability of fraud (Class 1)
        fraud_probability = prediction_result.get('fraud_probability', 0.0)
        risk_category = prediction_result.get('risk_category', 'Low')
        
        # Convert to percentage for display and storage
        risk_score_percent = fraud_probability * 100
        
        print(f"🤖 ML Prediction: Fraud Probability = {fraud_probability:.4f} ({risk_score_percent:.1f}%), Category = {risk_category}")
        
        # ========== STEP C: SAVE TO DATABASE ==========
        claim_id = str(uuid.uuid4())
        
        # Determine status based on fraud probability
        # High Risk: >= 0.7 (70%) -> flagged for investigation
        # Medium/Low Risk: < 0.7 (70%) -> submitted for review
        if fraud_probability >= 0.7:
            claim_status = 'flagged'
            current_stage = 'investigation'
        else:
            claim_status = 'submitted'
            current_stage = 'submission'
        
        conn = sqlite3.connect('claims.db')
        cursor = conn.cursor()
        
        # Insert into claims table with calculated risk and duration
        cursor.execute("""
            INSERT INTO claims 
            (id, user_id, status, current_stage, patient_age, diagnosis, claimed_amount, 
             admission_date, discharge_date, risk_score, risk_category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim_id,
            1,  # Default user_id (will be replaced with actual authenticated user in production)
            claim_status,
            current_stage,
            int(patient_age),
            diagnosis,
            float(amount_clean),
            admission_date,
            discharge_date,
            fraud_probability,  # Store as 0.0-1.0 probability
            risk_category,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Insert into training_data_verified table
        cursor.execute("""
            INSERT INTO training_data_verified 
            (patient_name, amount, date, extraction_score, extracted_text)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_name, float(amount_clean), admission_date, overall_score, extracted_text[:1000]))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Claim {claim_id} verified, analyzed, and saved (Status: {claim_status})")
        
        return {
            "success": True,
            "message": "Verified & Submitted",
            "claim_id": claim_id,
            "status": claim_status,
            "risk_score": round(risk_score_percent, 1),  # Return as percentage (0-100)
            "risk_category": risk_category,
            "duration_of_stay": duration,
            "fraud_probability": round(fraud_probability, 4),  # Also return raw probability
            "verification": {
                "name_match": name_score,
                "amount_found": amount_found,
                "overall_score": overall_score
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in submit_verified_claim: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Claim submission error: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting FastAPI Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)