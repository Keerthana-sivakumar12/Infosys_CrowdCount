"""
Admin Module - User Management
Handles user CRUD operations and user-related functionality
"""

from typing import List, Dict, Optional

# User database (in production, this would be in a real database)
users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "full_name": "Admin User",
        "role": "admin",
        "status": "active",
        "last_login": None
    },
    "user": {
        "id": 2,
        "username": "user",
        "full_name": "Regular User",
        "role": "user",
        "status": "active",
        "last_login": None
    }
}

def get_all_users() -> List[Dict]:
    """Get all users"""
    return list(users_db.values())

def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    return users_db.get(username)

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    for user in users_db.values():
        if user["id"] == user_id:
            return user
    return None

def create_user(username: str, full_name: str, role: str = "user") -> Dict:
    """Create a new user"""
    user_id = max([u["id"] for u in users_db.values()]) + 1
    new_user = {
        "id": user_id,
        "username": username,
        "full_name": full_name,
        "role": role,
        "status": "active",
        "last_login": None
    }
    users_db[username] = new_user
    return new_user

def update_user(username: str, **kwargs) -> Optional[Dict]:
    """Update user information"""
    user = users_db.get(username)
    if not user:
        return None
    
    # Update allowed fields
    allowed_fields = ["full_name", "role", "status"]
    for field in allowed_fields:
        if field in kwargs:
            user[field] = kwargs[field]
    
    return user

def delete_user(username: str) -> bool:
    """Delete a user"""
    if username in users_db:
        del users_db[username]
        return True
    return False

def update_last_login(username: str, login_time: str):
    """Update user's last login time"""
    user = users_db.get(username)
    if user:
        user["last_login"] = login_time
