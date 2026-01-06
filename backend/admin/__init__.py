"""
Admin Module
Provides admin-specific functionality including user, camera, and zone management
"""

from .user_management import (
    get_all_users,
    get_user_by_username,
    get_user_by_id,
    create_user,
    update_user,
    delete_user,
    update_last_login
)

from .camera_management import (
    get_all_cameras,
    get_camera_by_id,
    create_camera,
    update_camera,
    delete_camera,
    activate_camera,
    deactivate_camera
)

from .zone_management import (
    get_all_zones,
    get_zone_by_id,
    get_zone_by_name,
    create_zone,
    update_zone,
    delete_zone,
    get_zone_count,
    get_all_zone_counts
)

__all__ = [
    # User management
    'get_all_users',
    'get_user_by_username',
    'get_user_by_id',
    'create_user',
    'update_user',
    'delete_user',
    'update_last_login',
    
    # Camera management
    'get_all_cameras',
    'get_camera_by_id',
    'create_camera',
    'update_camera',
    'delete_camera',
    'activate_camera',
    'deactivate_camera',
    
    # Zone management
    'get_all_zones',
    'get_zone_by_id',
    'get_zone_by_name',
    'create_zone',
    'update_zone',
    'delete_zone',
    'get_zone_count',
    'get_all_zone_counts'
]
