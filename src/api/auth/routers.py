from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import sqlite3
from datetime import datetime

from .models import UserCreate, UserLogin, UserResponse, Token, TokenData
from .utils import verify_password, get_password_hash, create_access_token, decode_token
from ..database import get_db_connection

router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    user_id: int = payload.get("user_id")
    role: str = payload.get("role")
    
    if email is None or user_id is None:
        raise credentials_exception
    
    return TokenData(email=email, user_id=user_id, role=role)

def require_role(allowed_roles: list[str]):
    """Decorator to check user role"""
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user (customers only)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (email, full_name, password_hash, role, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (
            user_data.email,
            user_data.full_name,
            hashed_password,
            user_data.role,
            datetime.utcnow()
        ))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        # Fetch created user
        cursor.execute("""
            SELECT id, email, full_name, role, is_active, created_at
            FROM users WHERE id = ?
        """, (user_id,))
        
        user = cursor.fetchone()
        return UserResponse(
            id=user[0],
            email=user[1],
            full_name=user[2],
            role=user[3],
            is_active=user[4],
            created_at=user[5]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
    finally:
        conn.close()

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Authenticate user and return JWT token"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Fetch user by email
        cursor.execute("""
            SELECT id, email, full_name, password_hash, role, is_active, created_at
            FROM users WHERE email = ?
        """, (user_data.email,))
        
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(user_data.password, user[3]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user[5]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": user[1],  # email
                "user_id": user[0],
                "role": user[4]
            }
        )
        
        user_response = UserResponse(
            id=user[0],
            email=user[1],
            full_name=user[2],
            role=user[4],
            is_active=user[5],
            created_at=user[6]
        )
        
        return Token(access_token=access_token, user=user_response)
        
    finally:
        conn.close()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, email, full_name, role, is_active, created_at
            FROM users WHERE id = ?
        """, (current_user.user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user[0],
            email=user[1],
            full_name=user[2],
            role=user[3],
            is_active=user[4],
            created_at=user[5]
        )
        
    finally:
        conn.close()

@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}
