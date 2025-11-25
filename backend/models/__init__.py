# ============================================================================
# backend/models/__init__.py
# ============================================================================

"""
Database Models Package

All SQLAlchemy ORM models for the Sentinel AI Platform
"""

from backend.models.user import User, UserRole
from backend.models.camera import Camera
from backend.models.person import Person
from backend.models.detection import Detection
from backend.models.track import Track
from backend.models.watchlist import WatchlistEntry, WatchlistMatch, WatchlistType
from backend.models.alert import Alert
from backend.models.federated import FederatedNode, FederatedRound, FederatedUpdate

__all__ = [
    # User models
    "User",
    "UserRole",
    
    # Camera models
    "Camera",
    
    # Person tracking models
    "Person",
    "Detection",
    "Track",
    
    # Watchlist models
    "WatchlistEntry",
    "WatchlistMatch",
    "WatchlistType",
    
    # Alert models
    "Alert",
    
    # Federated learning models
    "FederatedNode",
    "FederatedRound",
    "FederatedUpdate",
]