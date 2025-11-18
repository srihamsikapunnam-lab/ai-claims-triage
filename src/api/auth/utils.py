import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import secrets
import hashlib

# JWT settings
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Truncate password to 72 bytes for bcrypt compatibility
    password_bytes = plain_password.encode('utf-8')[:72]

    # If the stored hash looks like a bcrypt hash, attempt bcrypt check
    try:
        if isinstance(hashed_password, str):
            hash_bytes = hashed_password.encode('utf-8')
        else:
            hash_bytes = hashed_password

        # bcrypt hashes start with $2b$, $2a$, $2y$, etc.
        if isinstance(hashed_password, str) and hashed_password.startswith('$2'):
            return bcrypt.checkpw(password_bytes, hash_bytes)
        else:
            # Fallback: support legacy SHA256 salted hashes stored as hex string
            # Legacy scheme (from older User model): sha256(password + salt)
            try:
                salt = "ai_claims_salt_2024"
                combined = (plain_password + salt).encode('utf-8')
                legacy_hash = hashlib.sha256(combined).hexdigest()
                return legacy_hash == (hashed_password if isinstance(hashed_password, str) else hashed_password.decode('utf-8'))
            except Exception:
                # As a last resort try bcrypt check (in case hash_bytes is valid)
                return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    # Truncate password to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
