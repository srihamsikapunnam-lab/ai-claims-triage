# CORS Fix & Deployment Guide

## ✅ Changes Made

### 1. Backend CORS Configuration Updated
**File**: `fastapi_server.py`

Added Netlify domain to allowed origins:
```python
allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "https://ai-claims.netlify.app",  # Your production frontend
    "https://*.netlify.app",  # Netlify preview deployments
]
```

### 2. Frontend API Configuration Updated
**Files**: 
- `frontend-react/src/utils/apiClient.js`
- `frontend-react/src/utils/authService.js`
- `frontend-react/netlify.toml`

Changed to use environment variable:
```javascript
const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";
```

## 🚀 Deployment Steps

### Step 1: Deploy Backend (Required First!)

Your backend needs to be publicly accessible. Options:

#### Option A: Deploy to Render (Recommended - Free Tier)
1. Go to https://render.com
2. Sign up/Login
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Configure:
   - **Name**: `ai-claims-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn fastapi_server:app --host 0.0.0.0 --port $PORT`
6. Click "Create Web Service"
7. Copy the deployment URL (e.g., `https://ai-claims-backend.onrender.com`)

#### Option B: Deploy to Railway
1. Go to https://railway.app
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Railway auto-detects Python
6. Copy the deployment URL

#### Option C: Deploy to Heroku
```bash
# Install Heroku CLI
heroku create ai-claims-backend
git push heroku main
heroku open
```

### Step 2: Update Netlify Environment Variable

1. Go to Netlify Dashboard: https://app.netlify.com
2. Select your site (`ai-claims`)
3. Go to **Site Settings** → **Environment Variables**
4. Add/Update:
   - **Key**: `REACT_APP_API_URL`
   - **Value**: `https://your-backend-url.com` (from Step 1)
5. Click **Save**

### Step 3: Redeploy Frontend

**Option A: Trigger Redeploy**
1. In Netlify Dashboard
2. Go to **Deploys**
3. Click **Trigger deploy** → **Clear cache and deploy site**

**Option B: Push to GitHub**
```bash
git add .
git commit -m "Fix CORS and update API URL"
git push origin main
```

Netlify will automatically rebuild.

### Step 4: Update Backend CORS (if backend URL changed)

If your backend URL is different from `https://ai-claims.onrender.com`, update `fastapi_server.py`:

```python
allow_origins=[
    # ... existing origins ...
    "https://your-actual-backend-url.com",
]
```

Then redeploy the backend.

## 🔧 Local Development

### Backend
```bash
cd ai-claims-triage
venv\Scripts\activate  # Windows
python fastapi_server.py
```

### Frontend
```bash
cd frontend-react
npm start
```

The `.env.local` file ensures `http://localhost:8000` is used locally.

## ✅ Verification

1. **Test CORS**: Open browser console on https://ai-claims.netlify.app
2. **Try Login**: Should no longer see CORS error
3. **Check Network**: In DevTools → Network tab, verify:
   - Request URL matches your backend
   - Response headers include `Access-Control-Allow-Origin`

## 🐛 Troubleshooting

### Still Getting CORS Error?

1. **Check Backend is Running**: Visit `https://your-backend-url.com/docs`
   - Should see FastAPI Swagger UI

2. **Verify Environment Variable**: In Netlify
   - Site Settings → Environment Variables
   - Confirm `REACT_APP_API_URL` is set correctly

3. **Check Backend Logs**: In Render/Railway dashboard
   - Look for startup errors
   - Verify CORS middleware is loaded

4. **Clear Browser Cache**: 
   - Hard refresh: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)
   - Or clear cache in DevTools

5. **Restart Backend**: Sometimes CORS changes need a restart

### Environment Variable Not Working?

- Netlify requires **full rebuild** after changing env vars
- Variable must start with `REACT_APP_` 
- Check spelling matches exactly in code

### Backend Connection Refused?

- Backend must be deployed to public URL
- Cannot use `localhost` or `127.0.0.1` in production
- Check backend is actually running (visit `/docs` endpoint)

## 📝 Current Configuration

**Frontend (Netlify)**: https://ai-claims.netlify.app
**Backend**: [SET THIS] - Deploy backend first!
**Environment Variable**: `REACT_APP_API_URL` = Your backend URL

---

**Next Steps:**
1. Deploy backend to Render/Railway/Heroku
2. Get backend URL
3. Set `REACT_APP_API_URL` in Netlify
4. Trigger redeploy
5. Test login on production site
