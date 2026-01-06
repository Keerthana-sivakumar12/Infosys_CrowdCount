"""
Authentication Module
Handles JWT authentication, user management, and role-based access control
"""

from .auth_service import (
    hash_password,
    verify_password,
    authenticate_user,
    create_access_token,
    decode_token,
    get_current_user,
    require_admin,
    Token,
    TokenData,
    LoginRequest,
    User,
    USERS_DB
)

__all__ = [
    'hash_password',
    'verify_password',
    'authenticate_user',
    'create_access_token',
    'decode_token',
    'get_current_user',
    'require_admin',
    'Token',
    'TokenData',
    'LoginRequest',
    'User',
    'USERS_DB'
]
