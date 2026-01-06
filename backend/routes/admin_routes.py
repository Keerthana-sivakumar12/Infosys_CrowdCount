"""
Admin Routes
Admin-only endpoints for managing users, cameras, zones, and settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from auth import auth_service as auth
    from admin import (
        get_all_users, get_user_by_username, create_user, update_user, delete_user,
        get_all_cameras, get_camera_by_id, create_camera, update_camera, delete_camera,
        get_all_zones, get_zone_by_id, create_zone, update_zone, delete_zone, get_all_zone_counts
    )
except ImportError:
    import auth
    from admin import user_management, camera_management, zone_management

router = APIRouter(prefix="/admin", tags=["Admin"])

# ==================== USER MANAGEMENT ====================

@router.get("/users")
def list_users(current_user: auth.User = Depends(auth.require_admin)):
    """Get all users (Admin only)"""
    return {"users": get_all_users()}

@router.get("/users/{username}")
def get_user(username: str, current_user: auth.User = Depends(auth.require_admin)):
    """Get user by username (Admin only)"""
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users")
def add_user(
    username: str,
    full_name: str,
    role: str = "user",
    current_user: auth.User = Depends(auth.require_admin)
):
    """Create new user (Admin only)"""
    if get_user_by_username(username):
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = create_user(username, full_name, role)
    return {"message": "User created successfully", "user": new_user}

@router.put("/users/{username}")
def modify_user(
    username: str,
    full_name: str = None,
    role: str = None,
    status: str = None,
    current_user: auth.User = Depends(auth.require_admin)
):
    """Update user (Admin only)"""
    updated_user = update_user(username, full_name=full_name, role=role, status=status)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully", "user": updated_user}

@router.delete("/users/{username}")
def remove_user(username: str, current_user: auth.User = Depends(auth.require_admin)):
    """Delete user (Admin only)"""
    if username == current_user.username:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    success = delete_user(username)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {username} deleted successfully"}

# ==================== CAMERA MANAGEMENT ====================

@router.get("/cameras")
def list_cameras(current_user: auth.User = Depends(auth.require_admin)):
    """Get all cameras (Admin only)"""
    return {"cameras": get_all_cameras()}

@router.get("/cameras/{camera_id}")
def get_camera(camera_id: int, current_user: auth.User = Depends(auth.require_admin)):
    """Get camera by ID (Admin only)"""
    camera = get_camera_by_id(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.post("/cameras")
def add_camera(
    name: str,
    source: str,
    location: str = "",
    current_user: auth.User = Depends(auth.require_admin)
):
    """Create new camera (Admin only)"""
    new_camera = create_camera(name, source, location)
    return {"message": "Camera created successfully", "camera": new_camera}

@router.put("/cameras/{camera_id}")
def modify_camera(
    camera_id: int,
    name: str = None,
    source: str = None,
    location: str = None,
    status: str = None,
    current_user: auth.User = Depends(auth.require_admin)
):
    """Update camera (Admin only)"""
    updated_camera = update_camera(camera_id, name=name, source=source, location=location, status=status)
    if not updated_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"message": "Camera updated successfully", "camera": updated_camera}

@router.delete("/cameras/{camera_id}")
def remove_camera(camera_id: int, current_user: auth.User = Depends(auth.require_admin)):
    """Delete camera (Admin only)"""
    success = delete_camera(camera_id)
    if not success:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"message": f"Camera {camera_id} deleted successfully"}

# ==================== ZONE MANAGEMENT ====================

@router.get("/zones")
def list_zones(current_user: auth.User = Depends(auth.require_admin)):
    """Get all zones (Admin only)"""
    zones = get_all_zones()
    counts = get_all_zone_counts()
    return {"zones": zones, "counts": counts}

@router.get("/zones/{zone_id}")
def get_zone(zone_id: int, current_user: auth.User = Depends(auth.require_admin)):
    """Get zone by ID (Admin only)"""
    zone = get_zone_by_id(zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone

@router.post("/zones")
def add_zone(
    name: str,
    points: List[List[int]],
    current_user: auth.User = Depends(auth.require_admin)
):
    """Create new zone (Admin only)"""
    new_zone = create_zone(name, points)
    return {"message": "Zone created successfully", "zone": new_zone}

@router.put("/zones/{zone_id}")
def modify_zone(
    zone_id: int,
    points: List[List[int]] = None,
    name: str = None,
    current_user: auth.User = Depends(auth.require_admin)
):
    """Update zone (Admin only)"""
    updated_zone = update_zone(zone_id, points=points, name=name)
    if not updated_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return {"message": "Zone updated successfully", "zone": updated_zone}

@router.delete("/zones/{zone_id}")
def remove_zone(zone_id: int, current_user: auth.User = Depends(auth.require_admin)):
    """Delete zone (Admin only)"""
    success = delete_zone(zone_id)
    return {"message": f"Zone {zone_id} deleted successfully"}

# ==================== THRESHOLD MANAGEMENT ====================

@router.post("/thresholds")
def set_zone_threshold(
    zone_name: str,
    max_capacity: int,
    current_user: auth.User = Depends(auth.require_admin)
):
    """Set threshold for a zone (Admin only)"""
    import database as db
    db.set_threshold(zone_name, max_capacity)
    return {"message": f"Threshold for {zone_name} set to {max_capacity}"}

@router.get("/thresholds")
def get_thresholds(current_user: auth.User = Depends(auth.get_current_user)):
    """Get all thresholds"""
    import database as db
    return db.get_all_thresholds()
