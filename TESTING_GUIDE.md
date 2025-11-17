# 🧪 Testing the Real Backend Integration

## Prerequisites
- Backend running on http://localhost:8000
- Frontend running on http://localhost:3000
- Database initialized with demo users

## Test Scenarios

### 1. **Test ML Model Prediction**

#### Steps:
1. Login as customer: `customer@demo.com` / `password123`
2. Navigate to "Submit Claim" tab
3. Fill out the form:
   ```
   Patient Age: 65
   Diagnosis: Heart Surgery
   Admission Date: 2024-01-01
   Discharge Date: 2024-01-05
   Claimed Amount: $45,000
   ```
4. Click "Submit Claim for AI Review"

#### Expected Results:
- ✅ Success message appears
- ✅ Claim ID displayed
- ✅ **AI Fraud Detection Results box shows:**
  - Risk Score: ~70-85% (high risk for large heart surgery claim)
  - Risk Category: "high"
  - Prediction: Shows model decision
  - Status: "manual_review" (auto-flagged for review)
- ✅ Warning message: "High risk detected - This claim will undergo manual review"

#### Backend Verification:
Check terminal for:
```
INFO: 127.0.0.1 - "POST /api/claims HTTP/1.1" 200 OK
```

Check database:
```bash
sqlite3 claims.db "SELECT id, risk_score, risk_category, status FROM claims ORDER BY created_at DESC LIMIT 1;"
```

---

### 2. **Test Low Risk Claim**

#### Steps:
Same as above but use:
```
Patient Age: 35
Diagnosis: Annual Checkup
Admission Date: 2024-01-10
Discharge Date: 2024-01-10
Claimed Amount: $250
```

#### Expected Results:
- ✅ Risk Score: ~15-25% (low risk)
- ✅ Risk Category: "low"
- ✅ Status: "under_review" (normal processing)
- ✅ Success message: "Low risk - Claim is being processed normally"

---

### 3. **Test Dashboard Real Data (Customer)**

#### Steps:
1. Login as customer
2. View "Dashboard" tab

#### Expected Results:
- ✅ Shows user's actual submitted claims (not mock data)
- ✅ Total Claims shows real count from database
- ✅ Recent Claims list displays actual submissions with:
  - Real claim IDs (UUID format)
  - Actual amounts
  - Real dates (today's date for new submissions)
  - ML-generated risk scores
- ✅ If no claims exist, counts show 0

---

### 4. **Test Company Dashboard (Admin)**

#### Steps:
1. Logout customer
2. Login as admin: `admin@demo.com` / `admin123`
3. View Dashboard

#### Expected Results:
- ✅ "All Claims" tab shows ALL claims in database (not just user's)
- ✅ Statistics show real counts:
  - Total Claims: actual DB count
  - Pending Review: real under_review count
  - High Risk: actual high risk claims
  - Approved/Rejected: real counts
- ✅ Performance Metrics section shows:
  - Real approval rate %
  - Actual total claim value
  - True average processing time
- ✅ Claims table shows all users' claims with real data

---

### 5. **Test API Endpoints Directly**

#### Get Dashboard Stats (requires auth token):
```bash
# First login to get token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.com","password":"admin123"}'

# Copy the access_token from response, then:
curl -X GET http://localhost:8000/api/company/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Expected Response:
```json
{
  "total_claims": 2,
  "pending_review": 1,
  "approved": 0,
  "rejected": 0,
  "high_risk": 1,
  "medium_risk": 0,
  "low_risk": 1,
  "avg_processing_time_hours": 0.0
}
```

#### Get All Claims:
```bash
curl -X GET http://localhost:8000/api/company/claims \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Expected Response:
Array of real claims with ML predictions:
```json
[
  {
    "id": "abc-123-...",
    "user_id": 1,
    "status": "manual_review",
    "patient_age": 65,
    "diagnosis": "Heart Surgery",
    "claimed_amount": 45000.0,
    "risk_score": 78.5,
    "risk_category": "high",
    "prediction": "fraudulent",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

---

### 6. **Test Error Handling**

#### Test with Backend Down:
1. Stop backend server (Ctrl+C in backend terminal)
2. Try to submit a claim in frontend

#### Expected Results:
- ✅ Error message appears: "Failed to submit claim"
- ✅ Form remains filled (data not lost)
- ✅ User can retry after restarting backend

#### Test with Invalid Token:
1. Clear localStorage in browser console: `localStorage.clear()`
2. Try to access dashboard

#### Expected Results:
- ✅ Redirects to login
- ✅ Shows authentication error

---

### 7. **Verify ML Model is Active**

#### Check Backend Startup Logs:
When backend starts, you should see:
```
✅ API-ready RandomForest model loaded successfully!
🎯 Model type: RandomForestClassifier
📊 Number of features: 8
📝 Features: ['patient_age', 'claimed_amount', 'length_of_stay', ...]
🔧 Encoders: ['gender', 'diagnosis']
✅ Real model ready for production predictions!
```

#### If Model Fails to Load:
Check for:
```
Warning: Could not load model service: [error message]
```
- Verify `models/fraud_model_api_ready.joblib` exists
- Check file permissions
- Ensure scikit-learn version matches

---

### 8. **Test Complete Workflow**

#### End-to-End Test:
1. **Customer submits claim**
   - Login as customer
   - Submit high-risk claim
   - Note the Claim ID
   - Verify risk score displayed

2. **Admin reviews claim**
   - Logout customer
   - Login as admin
   - Go to "All Claims" tab
   - Find the claim in table
   - Verify risk score matches
   - Click "View" (if implemented)

3. **Check database directly**
   ```bash
   sqlite3 claims.db "SELECT * FROM claims WHERE id='CLAIM_ID_HERE';"
   ```
   - Verify all fields populated
   - Check risk_score is not NULL
   - Confirm status is correct

4. **Check status history**
   ```bash
   sqlite3 claims.db "SELECT * FROM claim_status_history WHERE claim_id='CLAIM_ID_HERE';"
   ```
   - Verify initial status logged
   - Check timestamp is recent

---

## Success Criteria

✅ **Integration is working if:**
1. Claims submission triggers real ML prediction
2. Risk scores are calculated (not NULL or 0)
3. Dashboard shows actual database counts
4. Claims list displays real submissions
5. Status updates are persisted
6. Authentication protects all routes
7. Error messages appear for failures
8. Loading states show during API calls

❌ **Issues to check if:**
- Risk scores always show 0 or NULL → Model not loading
- Dashboard shows mock data → API calls failing
- Can't submit claims → CORS or auth issues
- See old data after refresh → Caching problem

---

## Debugging Tips

### Check Backend Logs:
```bash
# Terminal running backend should show:
INFO: 127.0.0.1 - "POST /api/claims HTTP/1.1" 200 OK
INFO: 127.0.0.1 - "GET /api/company/dashboard/stats HTTP/1.1" 200 OK
```

### Check Browser Console:
```javascript
// In browser dev tools (F12)
// Should NOT see:
"Failed to fetch"
"CORS error"
"401 Unauthorized" (unless not logged in)

// Should see:
"Fetching dashboard data..."
"Claim submitted successfully"
```

### Check Database:
```bash
# View all claims
sqlite3 claims.db "SELECT id, status, risk_score, risk_category FROM claims;"

# Count by status
sqlite3 claims.db "SELECT status, COUNT(*) FROM claims GROUP BY status;"

# View users
sqlite3 claims.db "SELECT email, role FROM users;"
```

### Verify Services:
```bash
# Backend running?
curl http://localhost:8000/health

# Frontend running?
curl http://localhost:3000

# Database exists?
ls -la claims.db
```

---

## Common Issues & Fixes

### "Failed to fetch" Error
**Cause:** Backend not running or CORS issue
**Fix:** 
1. Check backend is on port 8000
2. Verify CORS allows localhost:3000
3. Check no firewall blocking

### Risk Score Always NULL
**Cause:** ML model not loading
**Fix:**
1. Check `models/fraud_model_api_ready.joblib` exists
2. Reinstall scikit-learn: `pip install scikit-learn==1.7.2`
3. Check model_service.py imports

### Dashboard Shows 0 Claims
**Cause:** No claims in database or query failing
**Fix:**
1. Submit a test claim
2. Check database: `sqlite3 claims.db "SELECT COUNT(*) FROM claims;"`
3. Verify API endpoint returns data

### Authentication Loops
**Cause:** Token not being stored or invalid
**Fix:**
1. Clear localStorage: `localStorage.clear()`
2. Login again
3. Check token in dev tools → Application → Local Storage

---

## Performance Testing

### Load Test (Optional):
```bash
# Submit 10 claims rapidly
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/claims \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "patient_age": 45,
      "diagnosis": "Test '$i'",
      "admission_date": "2024-01-01",
      "discharge_date": "2024-01-02",
      "claimed_amount": 1000
    }'
done
```

Should handle without errors and ML model should predict on all.

---

## ✅ Final Verification

After testing all scenarios above, you should have:
- ✅ Multiple claims in database with varying risk scores
- ✅ Dashboard showing real statistics
- ✅ Claims list with actual data
- ✅ ML predictions working correctly
- ✅ Status updates persisting
- ✅ Authentication securing all endpoints

**The integration is complete and working!** 🎉
