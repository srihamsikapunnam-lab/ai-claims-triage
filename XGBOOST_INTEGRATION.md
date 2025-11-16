# XGBoost Model Integration & Claim Detail View - Implementation Summary

## 🎯 Overview
Complete integration of XGBoost model for fraud prediction with LIME explanations, removal of static risk displays, and addition of comprehensive claim detail view with approve/flag/reject actions.

## ✅ Completed Changes

### 1. **XGBoost Model Training Script**
**File:** `train_xgboost_model.py`

- Created comprehensive training script for XGBoost classifier
- Features:
  - Loads unified claims data from `data/processed/unified_claims_v1.csv`
  - Engineers 8 features: patient_age, claimed_amount, length_of_stay, claimed_per_day, high_amount_flag, short_stay_high_bill, gender_encoded, diagnosis_encoded
  - Handles class imbalance with `scale_pos_weight`
  - Trains XGBoost with 200 estimators, max_depth=6, learning_rate=0.1
  - Creates LIME explainer for interpretability
  - Saves model with all components to `models/xgboost_fraud_model.joblib` and `models/fraud_model_api_ready.joblib`

**To run:**
```bash
python train_xgboost_model.py
```

### 2. **Backend Model Service Updates**
**File:** `src/api/model_service.py`

**Changes:**
- Updated `load_model()` to support multiple model types (detects XGBoost vs RandomForest)
- Added `self.lime_explainer` to store LIME explainer
- Enhanced `predict()` method:
  - Generates LIME explanations with top 5 contributing features
  - Returns `lime_explanation` array with feature contributions
  - Returns structured status codes: `approved`, `under_review`, `rejected`, `flagged`
  - Includes `model_version` in response
- Improved `generate_explanations()`:
  - Uses LIME feature contributions for human-readable explanations
  - Provides context-aware risk descriptions
  - Includes actual values in explanations

### 3. **Database Schema Migration**
**File:** `migrate_database.py`

**New columns added to `claims` table:**
- `lime_explanation` (TEXT) - Stores JSON array of LIME feature contributions
- `model_version` (TEXT) - Tracks which model version made the prediction
- `length_of_stay` (INTEGER) - Calculated from admission/discharge dates

**To run:**
```bash
python migrate_database.py
```

### 4. **Backend API Models**
**File:** `src/api/workflows/models.py`

**Updated `ClaimDetailResponse` model:**
```python
class ClaimDetailResponse(ClaimResponse):
    admission_date: str
    discharge_date: str
    description: Optional[str] = None
    explanation: Optional[List[str]] = None
    lime_explanation: Optional[List[dict]] = None  # NEW
    full_name: Optional[str] = None               # NEW
    length_of_stay: Optional[int] = None          # NEW
    model_version: Optional[str] = None           # NEW
    status_history: List[dict] = []
```

### 5. **Backend API Routes**
**File:** `src/api/workflows/routers.py`

**Enhanced `create_claim` endpoint:**
- Calculates `length_of_stay` from admission/discharge dates
- Stores LIME explanations as JSON
- Stores model version
- Passes length_of_stay to prediction model

**Enhanced `get_claim_detail` endpoint:**
- Joins with `users` table to get `full_name`
- Returns LIME explanations parsed from JSON
- Returns all new fields (length_of_stay, model_version, full_name)

**Added `update_claim_status_simple` endpoint:**
- `PATCH /api/claims/{claim_id}/status`
- Accepts simple JSON: `{"status": "approved"/"rejected"/"flagged"}`
- Available to company_admin and company_staff roles only
- Adds entry to status history with timestamp and user info

### 6. **Frontend - Dashboard Component**
**File:** `frontend-react/src/components/Dashboard.js`

**Changes:**
- **Removed:** `RiskDisplay` component import and usage
- **Added:** React Router navigation support
- **Added:** Click handlers to navigate to claim detail view:
  - Recent claims are clickable
  - "View Details" button in all claims table
  - Navigates to `/claims/{claimId}`

### 7. **Frontend - ClaimForm Component**
**File:** `frontend-react/src/components/ClaimForm.js`

**Changes:**
- **Added:** React Router navigation with `useNavigate`
- **Removed:** Prediction result display (moved to detail view)
- **Added:** Automatic redirect to dashboard after successful submission
- Shows success message with "Redirecting to dashboard..." text
- Redirects after 1.5 seconds

### 8. **Frontend - ClaimDetail Component (NEW)**
**File:** `frontend-react/src/components/ClaimDetail.js`

**Features:**
- **Real-time AI Risk Assessment:**
  - Circular progress indicator showing risk score (0-100%)
  - Color-coded risk category (green/yellow/red)
  - Model prediction badge (Fraud/Legitimate)
  
- **LIME Explanations Visualization:**
  - Top 5 features ranked by importance
  - Visual bar charts showing contribution magnitude
  - Color coding: red for risk-increasing, green for risk-decreasing
  - Feature descriptions with actual values
  
- **Claim Information Display:**
  - Patient details, diagnosis, dates, amounts
  - Length of stay calculation
  - Status badge with color coding
  - Submission timestamp
  
- **Action Buttons (for staff/admin):**
  - ✅ Approve Claim
  - ❌ Reject Claim
  - 🚩 Flag for Manual Review
  - Buttons only visible for `company_admin` and `company_staff` roles
  - Buttons only enabled when status is `under_review`
  - Confirmation dialogs before action
  - Automatic refresh after status update

- **Human-Readable Explanations:**
  - Key findings from AI analysis
  - Context-aware risk descriptions
  - Model version display

**File:** `frontend-react/src/components/ClaimDetail.css`
- Comprehensive styling for claim detail view
- Responsive grid layout
- Circular progress indicator with conic gradient
- LIME feature cards with hover effects
- Color-coded risk levels and action buttons

### 9. **Frontend - App Routing**
**File:** `frontend-react/src/App.js`

**Changes:**
- Converted from view-based navigation to React Router
- **Added routes:**
  - `/` → redirects to `/dashboard`
  - `/dashboard` → Dashboard component
  - `/submit` → ClaimForm component
  - `/claims/:claimId` → ClaimDetail component (NEW)
- Updated navigation to use `<Link>` components
- Simplified navigation bar (removed unused tabs)

## 📊 Data Flow

### Claim Submission Flow:
1. User fills ClaimForm → POST `/api/claims`
2. Backend calculates length_of_stay
3. XGBoost model predicts with LIME explanation
4. Stores claim with lime_explanation JSON
5. Returns risk_score, prediction, lime_explanation
6. Frontend redirects to Dashboard

### Claim Detail View Flow:
1. User clicks claim → Navigate to `/claims/{id}`
2. ClaimDetail fetches GET `/api/claims/{id}`
3. Backend returns full claim data including LIME explanations
4. Frontend displays:
   - Risk score circular progress
   - LIME feature contributions as ranked list
   - Human-readable explanations
   - Action buttons (if authorized)

### Status Update Flow:
1. Staff clicks Approve/Reject/Flag button
2. Confirmation dialog
3. PATCH `/api/claims/{id}/status` with `{"status": "approved"}`
4. Backend updates claim status
5. Adds entry to status_history table
6. Frontend refreshes claim data
7. Shows success alert

## 🔧 Technical Implementation

### XGBoost Model Features:
```python
feature_columns = [
    'patient_age',          # Patient's age
    'claimed_amount',       # Total claim amount
    'length_of_stay',       # Hospital stay duration
    'claimed_per_day',      # Cost per day (calculated)
    'high_amount_flag',     # Binary: amount > 95th percentile
    'short_stay_high_bill', # Binary: stay < 2 days && amount > median
    'gender_encoded',       # Encoded gender
    'diagnosis_encoded'     # Encoded diagnosis code
]
```

### LIME Explanation Format:
```javascript
lime_explanation: [
  {
    "feature": "claimed_amount <= 5000.00",
    "contribution": 0.1234  // Positive = increases fraud risk
  },
  {
    "feature": "length_of_stay > 3.0",
    "contribution": -0.0567  // Negative = decreases fraud risk
  },
  ...
]
```

### Status Values:
- `under_review` - Initial status for most claims
- `approved` - Claim approved by staff
- `rejected` - Claim rejected by staff
- `flagged` - Marked for manual investigation

## 🚀 Deployment Steps

### 1. Train XGBoost Model:
```bash
python train_xgboost_model.py
```
Expected output:
- `models/xgboost_fraud_model.joblib`
- `models/fraud_model_api_ready.joblib`
- Test AUC > 0.70

### 2. Migrate Database:
```bash
python migrate_database.py
```
Adds: `lime_explanation`, `model_version`, `length_of_stay` columns

### 3. Install Frontend Dependencies:
```bash
cd frontend-react
npm install react-router-dom
```

### 4. Restart Backend:
```bash
python fastapi_server.py
```
Backend will automatically load XGBoost model

### 5. Restart Frontend:
```bash
cd frontend-react
npm start
```

## 🧪 Testing

### Test XGBoost Model:
1. Submit a high-risk claim:
   - Patient age: 65
   - Claimed amount: $45,000
   - Length of stay: 1 day
   - Expected: Risk score 70-85%, Fraud prediction

2. Submit a low-risk claim:
   - Patient age: 30
   - Claimed amount: $250
   - Length of stay: 1 day
   - Expected: Risk score 15-25%, Legitimate prediction

### Test Claim Detail View:
1. Login as customer → Submit claim
2. Navigate to Dashboard → Click on claim
3. Verify:
   - ✅ Risk score displays correctly
   - ✅ LIME explanations show top 5 features
   - ✅ Feature contributions are color-coded
   - ✅ Human-readable explanations appear
   - ✅ No action buttons (customer role)

4. Login as admin/staff → View same claim
5. Verify:
   - ✅ Action buttons appear
   - ✅ Approve button works
   - ✅ Reject button works
   - ✅ Flag button works
   - ✅ Status updates in real-time

### Test Navigation:
1. Submit claim → Verify redirect to dashboard
2. Click claim in recent claims → Verify navigation to detail
3. Click "View Details" in all claims table → Verify navigation
4. Click "Back to Dashboard" → Verify return to dashboard

## 📝 API Endpoints Summary

### New/Modified Endpoints:

**GET `/api/claims/{claim_id}`**
- Returns: Full claim details with LIME explanations
- Response includes: lime_explanation, model_version, length_of_stay, full_name
- Access: Customer (own claims), Staff/Admin (all claims)

**PATCH `/api/claims/{claim_id}/status`**
- Body: `{"status": "approved"/"rejected"/"flagged"}`
- Access: company_admin, company_staff only
- Creates status history entry
- Returns: Success message with new status

**POST `/api/claims`**
- Enhanced to store LIME explanations
- Calculates and stores length_of_stay
- Returns: Risk score with LIME data

## 🎨 UI/UX Improvements

### Dashboard:
- ❌ Removed static "AI Score Assessment" component
- ✅ Added clickable claim items
- ✅ "View Details" button in claims table
- ✅ Hover effects on claim cards

### Claim Submission:
- ✅ Clean success message
- ✅ Automatic redirect to dashboard (1.5s delay)
- ✅ No premature risk display

### Claim Detail:
- ✅ Professional circular progress indicator
- ✅ Ranked LIME feature list with visual bars
- ✅ Color-coded risk levels
- ✅ Contextual action buttons
- ✅ Responsive 2-column layout
- ✅ Smooth animations and transitions

## 🔐 Security & Access Control

### Role-Based Permissions:
- **Customer:**
  - Can view own claims only
  - Can submit new claims
  - Cannot see action buttons
  
- **Company Staff:**
  - Can view all claims
  - Can approve/reject/flag claims
  - Can see full LIME explanations
  
- **Company Admin:**
  - All staff permissions
  - Can access dashboard statistics
  - Can manage users (existing feature)

### Data Protection:
- User ID check on claim access
- JWT token verification on all endpoints
- Status updates logged with user ID and timestamp
- Cannot modify approved/rejected claims

## 📦 Files Modified/Created

### Created:
- `train_xgboost_model.py` - XGBoost training script
- `migrate_database.py` - Database schema migration
- `frontend-react/src/components/ClaimDetail.js` - Detail view component
- `frontend-react/src/components/ClaimDetail.css` - Detail view styling
- `XGBOOST_INTEGRATION.md` - This documentation

### Modified:
- `src/api/model_service.py` - XGBoost support, LIME integration
- `src/api/workflows/models.py` - Added new fields to ClaimDetailResponse
- `src/api/workflows/routers.py` - Enhanced endpoints, added PATCH endpoint
- `frontend-react/src/App.js` - React Router integration
- `frontend-react/src/components/Dashboard.js` - Removed RiskDisplay, added navigation
- `frontend-react/src/components/ClaimForm.js` - Added redirect functionality

## 🎓 Model Performance

### XGBoost Model Metrics:
- **Features:** 8 engineered features
- **Algorithm:** XGBoost Classifier
- **Estimators:** 200 trees
- **Max Depth:** 6
- **Learning Rate:** 0.1
- **Expected AUC:** 0.70-0.85

### LIME Explainability:
- **Num Features:** Top 5 most important
- **Mode:** Classification
- **Output:** Feature contribution scores (-1 to +1)
- **Interpretation:** Positive = increases fraud risk, Negative = decreases risk

## 🐛 Known Limitations

1. **Model Training Data:** Uses synthetic fraud labels based on patterns if real labels unavailable
2. **LIME Performance:** Explanation generation adds ~100-200ms to prediction time
3. **Frontend Routing:** Requires React Router DOM package (auto-installed)
4. **Database Migration:** Must run manually before using new features

## 🚧 Future Enhancements

1. **Real-time Updates:** WebSocket integration for live claim status updates
2. **Batch Processing:** Approve/reject multiple claims at once
3. **Advanced Filters:** Filter claims by date range, risk category, diagnosis
4. **Export Functionality:** Download LIME explanations as PDF report
5. **Model Monitoring:** Track model performance metrics over time
6. **A/B Testing:** Compare XGBoost vs RandomForest predictions
7. **Audit Trail:** Complete history of all actions taken on claims

## 📞 Support

If you encounter issues:
1. Check backend logs for model loading errors
2. Verify database migration completed successfully
3. Ensure XGBoost model file exists at `models/fraud_model_api_ready.joblib`
4. Check browser console for frontend routing errors
5. Verify JWT token is valid and roles are correct

---

**Implementation Date:** November 17, 2025
**Model Version:** XGBoost_Production_v2.0
**Status:** ✅ Complete and Ready for Testing
