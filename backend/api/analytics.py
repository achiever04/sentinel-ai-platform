# ============================================================================
# backend/api/analytics.py - Analytics API Routes
# ============================================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from backend.database import get_db
from backend.services.auth_service import get_current_active_user
from backend.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/detections/summary")
async def get_detection_summary(
    hours: int = 24,
    camera_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detection statistics summary"""
    from backend.models.person import Detection
    
    cutoff = datetime.now() - timedelta(hours=hours)
    query = db.query(Detection).filter(Detection.timestamp >= cutoff)
    
    if camera_id:
        query = query.filter(Detection.camera_id == camera_id)
    
    total_detections = query.count()
    
    # Count by emotion
    emotions = {}
    for detection in query.all():
        emotion = detection.emotion or 'unknown'
        emotions[emotion] = emotions.get(emotion, 0) + 1
    
    # Count masked/helmeted
    masked_count = query.filter(Detection.is_masked == True).count()
    helmeted_count = query.filter(Detection.is_helmeted == True).count()
    
    return {
        "total_detections": total_detections,
        "masked": masked_count,
        "helmeted": helmeted_count,
        "emotions": emotions,
        "time_window_hours": hours
    }

@router.get("/persons/activity")
async def get_person_activity(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get person activity trends"""
    from backend.models.person import Person
    
    cutoff = datetime.now() - timedelta(hours=hours)
    
    # Count unique persons
    unique_persons = db.query(Person).filter(
        Person.last_seen >= cutoff
    ).count()
    
    # Count watchlisted persons
    watchlisted = db.query(Person).filter(
        Person.last_seen >= cutoff,
        Person.is_watchlisted > 0
    ).count()
    
    return {
        "unique_persons": unique_persons,
        "watchlisted_persons": watchlisted,
        "time_window_hours": hours
    }

@router.get("/cameras/performance")
async def get_camera_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get camera performance metrics"""
    from backend.models.camera import Camera
    from backend.models.person import Detection
    
    cameras = db.query(Camera).all()
    performance = []
    
    for camera in cameras:
        detections_1h = db.query(Detection).filter(
            Detection.camera_id == camera.id,
            Detection.timestamp >= datetime.now() - timedelta(hours=1)
        ).count()
        
        performance.append({
            "camera_id": camera.id,
            "name": camera.name,
            "status": camera.status,
            "fps": camera.fps,
            "detections_last_hour": detections_1h
        })
    
    return {"cameras": performance}
