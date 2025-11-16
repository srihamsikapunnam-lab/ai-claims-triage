# AI Claims Triage System - Quick Start Guide

## 🚀 Running the Application Locally

### Prerequisites
- Python 3.8+ installed
- Node.js 14+ and npm installed
- Git (to clone the repository)

### One-Time Setup

1. **Install Python Dependencies**
   ```bash
   # Create virtual environment (if not exists)
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend-react
   npm install
   cd ..
   ```

3. **Initialize Database** (Optional - auto-runs on server start)
   ```bash
   cd src/api
   python init_enhanced_db.py
   cd ../..
   ```

### Starting the Application

**Option 1: Using Batch Files (Windows)**

Open TWO separate terminal windows:

**Terminal 1 - Backend:**
```batch
start_backend.bat
```

**Terminal 2 - Frontend:**
```batch
start_frontend.bat
```

**Option 2: Manual Start**

**Terminal 1 - Backend:**
```bash
# Activate venv first
venv\Scripts\activate

# Start backend
python -m uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend-react
npm start
```

### Access the Application

- **Frontend (React App):** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation (Swagger):** http://localhost:8000/docs
- **API Test Page:** http://localhost:8000/test

### Demo Accounts

Use these accounts to log in:

**Customer Account:**
- Email: `customer@demo.com`
- Password: `password123`
- Access: Submit claims, upload documents, view own claims

**Company Staff:**
- Email: `staff@demo.com`
- Password: `staff123`
- Access: View all claims, update claim status

**Company Admin:**
- Email: `admin@demo.com`
- Password: `admin123`
- Access: Full dashboard access including statistics

## 🎯 Key Features

### For Customers:
- ✅ Submit new insurance claims
- ✅ Upload supporting documents (PDF, images, DOCX)
- ✅ View claim status and history
- ✅ Get AI-powered fraud detection results with explanations

### For Company Staff:
- ✅ View all submitted claims
- ✅ Filter claims by status and stage
- ✅ Update claim status (approve, reject, request more info)
- ✅ View complete claim history

### For Company Admins:
- ✅ All staff features
- ✅ Dashboard with statistics (total claims, pending, approved, rejected)
- ✅ Analytics and reporting

## 🔧 Troubleshooting

### "Failed to fetch" Error

If you see this error in the frontend:

1. **Check if backend is running:**
   - Open http://localhost:8000/health in browser
   - Should see: `{"status": "healthy", "service": "fastapi", "version": "2.0"}`

2. **Verify ports are not blocked:**
   ```powershell
   # Check if port 8000 is in use
   netstat -ano | findstr :8000
   
   # Check if port 3000 is in use
   netstat -ano | findstr :3000
   ```

3. **Restart both servers:**
   - Close both terminal windows
   - Start backend first, wait for it to fully load
   - Then start frontend

4. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Or clear browser cache completely

### Port Already in Use

If you get "port already in use" error:

```powershell
# Find process using the port
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Database Not Found

If you get database errors:

```bash
cd src/api
python init_enhanced_db.py
```

This will recreate the database with demo users.

## 📁 Project Structure

```
ai-claims-triage/
├── fastapi_server.py          # Main backend server
├── start_backend.bat          # Backend startup script
├── start_frontend.bat         # Frontend startup script
├── requirements.txt           # Python dependencies
├── claims.db                  # SQLite database (created on first run)
│
├── src/
│   └── api/
│       ├── auth/              # Authentication system
│       ├── documents/         # Document upload/management
│       ├── workflows/         # Claim processing workflows
│       └── model_service.py   # ML fraud detection
│
├── frontend-react/
│   ├── package.json
│   └── src/
│       ├── components/        # React components
│       ├── contexts/          # State management
│       └── utils/             # API clients
│
└── models/                    # Trained ML models
    └── fraud_model_api_ready.joblib
```

## 🔐 Security Notes

- JWT tokens expire after 24 hours
- Passwords are hashed using bcrypt (12 rounds)
- Role-based access control (customer, staff, admin)
- CORS configured for localhost:3000 only

## 📊 API Endpoints

### Authentication
- POST `/api/auth/register` - Register new customer
- POST `/api/auth/login` - Login and get JWT token
- GET `/api/auth/me` - Get current user info
- POST `/api/auth/logout` - Logout

### Claims
- POST `/api/claims` - Submit new claim (triggers AI prediction)
- GET `/api/claims` - Get user's claims
- GET `/api/claims/{id}` - Get claim details
- PUT `/api/claims/{id}/status` - Update claim status (staff only)

### Documents
- POST `/api/claims/{id}/documents` - Upload document
- GET `/api/claims/{id}/documents` - List claim documents
- GET `/api/documents/{id}` - Download document
- DELETE `/api/documents/{id}` - Delete document

### Company Dashboard (Staff/Admin only)
- GET `/api/company/claims` - Get all claims with filters
- GET `/api/company/dashboard/stats` - Get dashboard statistics

## 🛠️ Development

### Running Tests
```bash
# Backend tests
pytest

# Frontend tests
cd frontend-react
npm test
```

### Code Quality
```bash
# Python linting
flake8 src/

# Frontend linting
cd frontend-react
npm run lint
```

## 📝 License

This project is for educational purposes.

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure both backend and frontend are running
4. Check browser console for detailed errors (F12)
5. Review backend logs in the terminal

---

**Last Updated:** November 2025
**Version:** 2.0
