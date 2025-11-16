# AI Claims Triage System - Enhanced Version 2.0

## 🚀 New Features

### 1. **User Authentication System**
- JWT token-based authentication
- Role-based access control:
  - **Customer**: Submit claims, upload documents, view own claims
  - **Company Staff**: View all claims, update claim status
  - **Company Admin**: Full system access
- Secure password hashing with bcrypt
- Auto-logout on token expiration

### 2. **Document Upload & Management**
- Multiple document uploads per claim
- Supported formats: PDF, PNG, JPG, JPEG, DOC, DOCX
- Document categorization (medical reports, bills, prescriptions, etc.)
- Secure file storage with authentication
- Drag-and-drop upload interface
- File size validation (max 10MB)

### 3. **Claim Processing Workflow**
- Automated status tracking:
  - Submitted → Under Review → Approved/Rejected/Manual Review
- Status history with timestamps
- High-risk claims automatically flagged for manual review
- Timeline view showing current processing stage
- Company dashboard for claim management

### 4. **Enhanced Company Dashboard**
- View all claims with filtering (status, risk score, category)
- Real-time statistics:
  - Total claims, pending review, approval rate
  - Risk distribution (high/medium/low)
  - Average processing time
- Access to AI fraud detection explanations (LIME)
- Document viewing for each claim
- Manual decision-making interface

## 📦 Installation & Setup

### Backend Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Initialize the enhanced database:**
```bash
cd src/api
python init_enhanced_db.py
```

This will create:
- Users table with roles
- Enhanced claims table with workflow fields
- Documents table
- Claim status history table
- Demo user accounts

3. **Start the FastAPI server:**
```bash
python fastapi_server.py
```

The server will run on `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend-react
npm install
```

2. **Start the React development server:**
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## 🔐 Demo Accounts

The system comes with pre-configured demo accounts:

| Role | Email | Password |
|------|-------|----------|
| Customer | customer@demo.com | password123 |
| Company Admin | admin@demo.com | admin123 |
| Company Staff | staff@demo.com | staff123 |

## 🌟 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user (customer)
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user

### Claims & Workflow
- `POST /api/claims` - Create new claim (customer)
- `GET /api/claims` - Get user's claims
- `GET /api/claims/{claim_id}` - Get claim details
- `GET /api/claims/{claim_id}/status` - Get claim status
- `PUT /api/claims/{claim_id}/status` - Update claim status (company staff)

### Documents
- `POST /api/claims/{claim_id}/documents` - Upload document
- `GET /api/claims/{claim_id}/documents` - List claim documents
- `GET /api/documents/{document_id}/download` - Download document
- `DELETE /api/documents/{document_id}` - Delete document

### Company Dashboard
- `GET /api/company/claims` - Get all claims with filters
- `GET /api/company/dashboard/stats` - Get dashboard statistics

## 🎯 Usage Workflow

### For Customers:
1. Register/Login
2. Submit a new medical insurance claim
3. Upload supporting documents (medical reports, bills, etc.)
4. Track claim status in real-time
5. View AI risk assessment and explanations
6. Receive approval/rejection notifications

### For Company Staff:
1. Login with company credentials
2. View all submitted claims
3. Filter by status, risk score, or category
4. Review high-risk claims flagged by AI
5. Access uploaded documents
6. Update claim status (approve/reject/request more info)
7. View processing statistics

## 🛠️ Technical Architecture

### Backend (FastAPI)
```
src/api/
├── auth/               # Authentication module
│   ├── models.py       # User models
│   ├── utils.py        # JWT & password utilities
│   └── routers.py      # Auth endpoints
├── documents/          # Document management
│   ├── models.py       # Document models
│   ├── storage.py      # File storage utilities
│   └── routers.py      # Document endpoints
├── workflows/          # Claim workflow
│   ├── models.py       # Claim & status models
│   └── routers.py      # Claim endpoints
└── init_enhanced_db.py # Database initialization
```

### Frontend (React)
```
src/
├── components/
│   ├── Auth/           # Login/Register components
│   ├── Documents/      # Document upload component
│   ├── ClaimForm.js    # Enhanced claim submission
│   └── Dashboard.js    # User dashboard
├── contexts/
│   └── AuthContext.js  # Authentication state management
└── utils/
    ├── authService.js  # Auth API client
    └── apiClient.js    # General API client
```

### Database Schema
- **users**: User accounts with roles
- **claims**: Claims with AI predictions and workflow status
- **documents**: Uploaded documents linked to claims
- **claim_status_history**: Audit trail of status changes

## 🔒 Security Features

1. **JWT Authentication**: Secure token-based auth with expiration
2. **Password Hashing**: Bcrypt with salt for password storage
3. **Role-Based Access Control**: Endpoint protection by user role
4. **File Validation**: Type and size checks for uploads
5. **Secure File Storage**: Authentication required for document access
6. **CORS Configuration**: Controlled cross-origin requests

## 📊 AI Fraud Detection

The system maintains all original AI capabilities:
- Random Forest model trained on Medicare data
- LIME (Local Interpretable Model-agnostic Explanations)
- Risk scoring (0-100)
- Risk categorization (low/medium/high)
- Feature importance analysis

High-risk claims (score ≥ 70) are automatically flagged for manual review.

## 🧪 Testing

### Test Customer Flow:
1. Register as a new customer
2. Submit a claim with medical details
3. Upload documents (medical report, bill)
4. Check AI risk assessment
5. Track claim status

### Test Company Flow:
1. Login as company admin/staff
2. View all claims in dashboard
3. Filter by high-risk claims
4. Review documents
5. Update claim status
6. View statistics

## 📝 Environment Variables

Create a `.env` file (optional):
```
API_BASE_URL=http://localhost:8000
REACT_APP_API_URL=http://localhost:8000/api
```

## 🐛 Troubleshooting

**Issue**: "Module not found: passlib/jose"
**Solution**: Run `pip install passlib[bcrypt] python-jose[cryptography]`

**Issue**: "Database locked"
**Solution**: Close any open database connections and restart the server

**Issue**: "CORS error"
**Solution**: Verify CORS middleware is enabled in `fastapi_server.py`

**Issue**: "File upload fails"
**Solution**: Check `uploads/documents` directory exists and has write permissions

## 🚀 Next Steps

Potential enhancements:
- Email notifications for status changes
- Real-time updates with WebSockets
- Advanced analytics dashboard
- Bulk claim processing
- Mobile app (React Native)
- Cloud storage integration (AWS S3)
- OCR for document text extraction

## 📞 Support

For issues or questions:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review error messages in browser console and server logs
3. Verify database initialization completed successfully

## 📜 License

This enhanced system builds upon the original AI Claims Triage project with added enterprise features for production deployment.
