# ============================================================================
# backend/tasks/__init__.py
# ============================================================================

"""
Background Tasks Package

Celery tasks for asynchronous processing
"""

from backend.tasks.celery_app import celery_app

__all__ = [
    "celery_app",
]

# Task imports for Celery autodiscovery
from backend.tasks import video_tasks
from backend.tasks import alert_tasks
from backend.tasks import federated_tasks