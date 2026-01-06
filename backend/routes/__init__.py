"""
Routes Module
Centralized API route management
"""

from .auth_routes import router as auth_router
from .admin_routes import router as admin_router
from .analytics_routes import router as analytics_router
from .public_routes import router as public_router

__all__ = [
    'auth_router',
    'admin_router',
    'analytics_router',
    'public_router'
]
