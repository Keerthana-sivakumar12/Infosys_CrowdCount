"""
Admin Module - Camera Management
Handles camera configuration and management
"""

from typing import List, Dict, Optional

# Camera database (in production, this would be in a real database)
cameras_db = {
    1: {
        "id": 1,
        "name": "Main Camera",
        "source": 0,  # Webcam index or video file path
        "location": "Main Entrance",
        "status": "active",
        "resolution": "1280x720",
        "fps": 30
    }
}

def get_all_cameras() -> List[Dict]:
    """Get all cameras"""
    return list(cameras_db.values())

def get_camera_by_id(camera_id: int) -> Optional[Dict]:
    """Get camera by ID"""
    return cameras_db.get(camera_id)

def create_camera(name: str, source, location: str = "") -> Dict:
    """Create a new camera"""
    camera_id = max(cameras_db.keys()) + 1 if cameras_db else 1
    new_camera = {
        "id": camera_id,
        "name": name,
        "source": source,
        "location": location,
        "status": "active",
        "resolution": "1280x720",
        "fps": 30
    }
    cameras_db[camera_id] = new_camera
    return new_camera

def update_camera(camera_id: int, **kwargs) -> Optional[Dict]:
    """Update camera information"""
    camera = cameras_db.get(camera_id)
    if not camera:
        return None
    
    # Update allowed fields
    allowed_fields = ["name", "source", "location", "status", "resolution", "fps"]
    for field in allowed_fields:
        if field in kwargs:
            camera[field] = kwargs[field]
    
    return camera

def delete_camera(camera_id: int) -> bool:
    """Delete a camera"""
    if camera_id in cameras_db:
        del cameras_db[camera_id]
        return True
    return False

def activate_camera(camera_id: int) -> bool:
    """Activate a camera"""
    camera = cameras_db.get(camera_id)
    if camera:
        camera["status"] = "active"
        return True
    return False

def deactivate_camera(camera_id: int) -> bool:
    """Deactivate a camera"""
    camera = cameras_db.get(camera_id)
    if camera:
        camera["status"] = "inactive"
        return True
    return False
