"""API routes package"""

# Import all route modules
from backend.api import (
    auth,
    cameras,
    persons,
    watchlist,
    alerts,
    analytics,
    federated,
    uploads
)

__all__ = [
    "auth",
    "cameras",
    "persons",
    "watchlist",
    "alerts",
    "analytics",
    "federated",
    "uploads"
]
