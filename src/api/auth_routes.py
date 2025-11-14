from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import secrets
from datetime import datetime, timedelta

# Import our database user model
from .db_user import db_user

router = APIRouter()

# Simple token storage
active_tokens = {}

@router.post("/register")
async def register(user_data: Dict[str, Any]):
    """Register a new user in database"""
    try:
        # Check if required fields are provided
        if not user_data.get('username') or not user_data.get('password'):
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        # Create user in database
        user_id = db_user.create_user(
            username=user_data['username'],
            email=user_data.get('email', ''),
            password=user_data['password'],
            role=user_data.get('role', 'user')
        )
        
        # Get the created user
        user = db_user.get_user_by_username(user_data['username'])
        
        print(f"✅ New user registered in DATABASE: {user['username']} (ID: {user_id})")
        
        return {
            "status": "success",
            "message": "User registered successfully in database",
            "user": user
        }
        
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=400, detail="Username or email already exists")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login")
async def login(login_data: Dict[str, Any]):
    """Login user and return token"""
    try:
        username = login_data.get('username')
        password = login_data.get('password')
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        # Verify user against DATABASE
        user = db_user.verify_user(username, password)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Generate simple token
        token = secrets.token_hex(16)
        
        # Store token
        active_tokens[token] = {
            "user_id": user["id"],
            "username": user["username"],
            "expires": datetime.now() + timedelta(hours=24)
        }
        
        print(f"✅ User logged in from DATABASE: {user['username']}")
        
        return {
            "status": "success",
            "message": "Login successful (database)",
            "token": token,
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/me")
async def get_current_user(token: str):
    """Get current user info using token"""
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    token_data = active_tokens[token]
    
    # Find user in DATABASE
    user = db_user.get_user_by_username(token_data["username"])
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found in database")
    
    return {
        "status": "success",
        "user": user
    }

@router.post("/logout")
async def logout(token: str):
    """Logout user by removing token"""
    if token in active_tokens:
        username = active_tokens[token]["username"]
        del active_tokens[token]
        return {"status": "success", "message": f"User {username} logged out successfully"}
    else:
        return {"status": "success", "message": "Already logged out"}

print("✅ DATABASE Auth routes loaded successfully!")