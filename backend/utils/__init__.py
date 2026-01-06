"""
Utilities Module
Helper functions and common utilities
"""

import datetime
import json
from typing import Any, Dict

def format_timestamp(dt: datetime.datetime = None) -> str:
    """Format datetime to string"""
    if dt is None:
        dt = datetime.datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_timestamp(ts_str: str) -> datetime.datetime:
    """Parse timestamp string to datetime"""
    return datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}

def safe_json_dumps(obj: Any) -> str:
    """Safely dump object to JSON string"""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return "{}"

def validate_zone_points(points: list) -> bool:
    """Validate zone points format"""
    if not isinstance(points, list) or len(points) < 3:
        return False
    
    for point in points:
        if not isinstance(point, list) or len(point) != 2:
            return False
        if not all(isinstance(coord, (int, float)) for coord in point):
            return False
    
    return True

__all__ = [
    'format_timestamp',
    'parse_timestamp',
    'safe_json_loads',
    'safe_json_dumps',
    'validate_zone_points'
]
