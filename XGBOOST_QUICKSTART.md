# 🚀 Quick Start Guide - XGBoost Integration

## Prerequisites
- Python environment with venv activated
- Node.js and npm installed
- Backend running on port 8000
- Frontend running on port 3000

## Step-by-Step Setup

### 1️⃣ Train XGBoost Model (5 minutes)
```bash
# From project root
python train_xgboost_model.py
```
**Expected output:**
```
✅ Loaded data: (shape)
✅ XGBoost model trained!
🎯 Test AUC: 0.XXXX
✅ Model saved to: models/xgboost_fraud_model.joblib
```

### 2️⃣ Migrate Database (1 minute)
```bash
python migrate_database.py
```
**Expected output:**
```
✅ Added lime_explanation column
✅ Added model_version column
✅ Added length_of_stay column
✅ Database migration completed successfully!
```

### 3️⃣ Install Frontend Dependencies (2 minutes)
```bash
cd frontend-react
npm install react-router-dom
```

### 4️⃣ Restart Backend (1 minute)
```bash
# Stop current backend (Ctrl+C)
# From project root
python fastapi_server.py
```
**Look for:**
```
✅ API-ready model loaded successfully!
🎯 Model type: XGBClassifier
🕵️ LIME explainer: ✅ Loaded
```

### 5️⃣ Restart Frontend (1 minute)
```bash
# Stop current frontend (Ctrl+C)
cd frontend-react
npm start
```
**Opens:** http://localhost:3000

## ✅ Verification Checklist

### Backend Verification:
- [ ] Backend starts without errors
- [ ] Logs show "XGBClassifier" loaded
- [ ] Logs show "LIME explainer: ✅ Loaded"
- [ ] GET http://localhost:8000/health returns 200 OK

### Frontend Verification:
- [ ] Frontend loads without errors
- [ ] Can login with demo credentials
- [ ] Dashboard displays (no RiskDisplay component)
- [ ] Navigation bar shows Dashboard and Submit Claim

## 🧪 Quick Test Workflow

### Test 1: Submit High-Risk Claim
1. Login as customer: `customer@demo.com` / `password123`
2. Click "Submit Claim"
3. Fill form:
   - Patient Age: **65**
   - Claimed Amount: **$45,000**
   - Diagnosis: **Heart Surgery**
   - Admission Date: Today
   - Discharge Date: Tomorrow (1 day stay)
4. Submit
5. **Expected:** Redirects to dashboard after 1.5 seconds

### Test 2: View Claim Details
1. On Dashboard, click on the claim you just submitted
2. **Verify you see:**
   - ✅ Circular risk score indicator (70-85%)
   - ✅ Risk category "High" or "Very High"
   - ✅ LIME Explanations section with 5 features
   - ✅ Feature bars (red for risk-increasing)
   - ✅ Key findings with explanations
   - ✅ NO action buttons (customer role)

### Test 3: Staff Actions
1. Logout → Login as staff: `staff@demo.com` / `staff123`
2. Go to Dashboard → Click same claim
3. **Verify you see:**
   - ✅ Same risk assessment and LIME explanations
   - ✅ Three action buttons: Approve, Reject, Flag
   - ✅ Buttons are enabled (status is under_review)
4. Click "🚩 Flag for Manual Review"
5. Confirm dialog
6. **Expected:** Success message, status updates to "FLAGGED"

### Test 4: Low-Risk Claim
1. Login as customer
2. Submit claim:
   - Patient Age: **30**
   - Claimed Amount: **$250**
   - Diagnosis: **Routine Checkup**
   - Length of Stay: 1 day
3. View claim details
4. **Expected:** 
   - Risk score 15-30%
   - Prediction "Legitimate"
   - Green color indicators

## 🐛 Troubleshooting

### Backend Issues:

**Problem:** "Model file not found"
```bash
# Solution: Train the model first
python train_xgboost_model.py
```

**Problem:** "Column lime_explanation does not exist"
```bash
# Solution: Run migration
python migrate_database.py
```

**Problem:** "ModuleNotFoundError: No module named 'xgboost'"
```bash
# Solution: Install xgboost
pip install xgboost lime
```

### Frontend Issues:

**Problem:** "useNavigate() may be used only in the context of a <Router>"
```bash
# Solution: Install react-router-dom
cd frontend-react
npm install react-router-dom
```

**Problem:** Claim detail page shows 404
```bash
# Solution: Verify backend is running and claim ID is valid
# Check browser console for API errors
```

**Problem:** Action buttons don't appear
- Verify you're logged in as staff or admin (not customer)
- Check claim status is "under_review"
- Open browser console and check user role

## 📊 Expected API Responses

### POST /api/claims (after XGBoost integration):
```json
{
  "id": "uuid-here",
  "user_id": 1,
  "status": "under_review",
  "patient_age": 65,
  "diagnosis": "Heart Surgery",
  "claimed_amount": 45000,
  "risk_score": 78,
  "risk_category": "High",
  "prediction": "Fraud",
  "created_at": "2025-11-17T...",
  "updated_at": "2025-11-17T..."
}
```

### GET /api/claims/{id} (with LIME):
```json
{
  "id": "uuid-here",
  "full_name": "John Doe",
  "patient_age": 65,
  "diagnosis": "Heart Surgery",
  "claimed_amount": 45000,
  "length_of_stay": 1,
  "risk_score": 78,
  "risk_category": "High",
  "prediction": "Fraud",
  "explanation": [
    "Primary risk factor: claimed_amount (contributes +0.45 to fraud score)",
    "Claim amount ($45,000.00) significantly exceeds typical range",
    "Short stay (1 days) with high billing detected"
  ],
  "lime_explanation": [
    {"feature": "claimed_amount > 20000.00", "contribution": 0.4523},
    {"feature": "length_of_stay <= 2.0", "contribution": 0.2341},
    {"feature": "patient_age > 60.0", "contribution": 0.1234},
    {"feature": "short_stay_high_bill > 0.5", "contribution": 0.0987},
    {"feature": "high_amount_flag > 0.5", "contribution": 0.0654}
  ],
  "model_version": "XGBClassifier_Production_v2.0",
  "status": "under_review",
  "status_history": [...]
}
```

---

**Total Setup Time:** ~10 minutes
**Status:** Ready for Production Testing ✅
