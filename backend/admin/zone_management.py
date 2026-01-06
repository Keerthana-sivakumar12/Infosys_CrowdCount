"""
Admin Module - Zone Management
Handles zone CRUD operations for admin
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import List, Dict, Optional

# Import from services
try:
    from services import zones as zone_service
except ImportError:
    # Fallback to old import
    import zones as zone_service

def get_all_zones() -> List[Dict]:
    """Get all zones"""
    return zone_service.zones

def get_zone_by_id(zone_id: int) -> Optional[Dict]:
    """Get zone by ID"""
    for zone in zone_service.zones:
        if zone["id"] == zone_id:
            return zone
    return None

def get_zone_by_name(zone_name: str) -> Optional[Dict]:
    """Get zone by name"""
    for zone in zone_service.zones:
        if zone["name"] == zone_name:
            return zone
    return None

def create_zone(name: str, points: List[List[int]]) -> Dict:
    """Create a new zone"""
    zone_service.add_zone(name, points)
    zone_service.save_zones()
    return get_zone_by_name(name)

def update_zone(zone_id: int, points: List[List[int]] = None, name: str = None) -> Optional[Dict]:
    """Update zone"""
    zone = get_zone_by_id(zone_id)
    if not zone:
        return None
    
    if points:
        zone_service.update_zone(zone_id, points)
    
    if name:
        zone["name"] = name
    
    zone_service.save_zones()
    return zone

def delete_zone(zone_id: int) -> bool:
    """Delete zone"""
    zone_service.delete_zone_by_id(zone_id)
    zone_service.save_zones()
    return True

def get_zone_count(zone_id: int) -> int:
    """Get current people count in zone"""
    count = len(zone_service.zone_current_inside.get(zone_id, set()))
    return count

def get_all_zone_counts() -> Dict[str, int]:
    """Get counts for all zones"""
    counts = {}
    for zone in zone_service.zones:
        zone_id = zone["id"]
        zone_name = zone["name"]
        counts[zone_name] = get_zone_count(zone_id)
    return counts
