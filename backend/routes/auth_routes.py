"""
Authentication Routes
Handles login, logout, and authentication-related endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from auth import auth_service as auth
except ImportError:
    import auth as auth

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

@router.post("/login", response_model=auth.Token)
def login(login_data: auth.LoginRequest):
    """
    User login endpoint
    Returns JWT token with user role
    """
    user = auth.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"]
    }

@router.post("/logout")
def logout(current_user: auth.User = Depends(auth.get_current_user)):
    """
    User logout endpoint
    (Token invalidation handled client-side)
    """
    return {"message": f"User {current_user.username} logged out successfully"}

@router.get("/me")
def get_current_user_info(current_user: auth.User = Depends(auth.get_current_user)):
    """
    Get current authenticated user information
    """
    return {
        "username": current_user.username,
        "role": current_user.role,
        "full_name": current_user.full_name
    }

@router.post("/verify")
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify JWT token validity
    """
    try:
        token = credentials.credentials
        token_data = auth.decode_token(token)
        return {
            "valid": True,
            "username": token_data.username,
            "role": token_data.role
        }
    except HTTPException:
        return {"valid": False}
