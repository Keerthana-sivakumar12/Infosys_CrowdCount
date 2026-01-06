from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Security configuration
SECRET_KEY = "crowdcount-infosys-secret-key-2025-secure-jwt-token"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# User database with hashed passwords (SHA-256 for demo, use bcrypt in production)
# Passwords are hashed with SHA-256 + salt
SALT = "crowdcount_salt_2025"

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    return hashlib.sha256((password + SALT).encode()).hexdigest()

USERS_DB = {
    "admin": {
        "username": "admin",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "full_name": "Admin User"
    },
    "user": {
        "username": "user",
        "password_hash": hash_password("user123"),
        "role": "user",
        "full_name": "Regular User"
    }
}

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    role: str
    full_name: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password

def authenticate_user(username: str, password: str):
    """Authenticate user credentials"""
    user = USERS_DB.get(username)
    if not user:
        return False
    
    if not verify_password(password, user["password_hash"]):
        return False
    
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return TokenData(username=username, role=role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from token"""
    token = credentials.credentials
    token_data = decode_token(token)
    user = USERS_DB.get(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return User(
        username=user["username"],
        role=user["role"],
        full_name=user["full_name"]
    )

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role for endpoint access"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
