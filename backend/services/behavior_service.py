# ============================================================================
# backend/services/behavior_service.py - Behavior Analysis Service
# ============================================================================

from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta
from backend.models.person import Person
from backend.models.track import Track
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class BehaviorService:
    """Service for analyzing person behavior patterns"""
    
    @staticmethod
    def get_suspicious_activities(
        db: Session,
        hours: int = 24,
        min_anomaly_score: float = 0.7
    ) -> List[Dict]:
        """Get suspicious activities within time window"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        suspicious_tracks = db.query(Track, Person).join(
            Person, Track.person_id == Person.id
        ).filter(
            Track.start_time >= cutoff,
            Track.is_suspicious == True,
            Track.anomaly_score >= min_anomaly_score
        ).all()
        
        activities = []
        for track, person in suspicious_tracks:
            activities.append({
                "person_id": person.person_id,
                "behavior_type": track.behavior_type,
                "anomaly_score": track.anomaly_score,
                "start_time": track.start_time.isoformat(),
                "end_time": track.end_time.isoformat() if track.end_time else None,
                "camera_id": track.camera_id
            })
        
        return activities
    
    @staticmethod
    def get_loitering_events(
        db: Session,
        min_duration_seconds: int = 300,
        hours: int = 24
    ) -> List[Dict]:
        """Get loitering events (standing in one place too long)"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        loitering = db.query(Track, Person).join(
            Person, Track.person_id == Person.id
        ).filter(
            Track.start_time >= cutoff,
            Track.behavior_type == 'standing'
        ).all()
        
        events = []
        for track, person in loitering:
            if track.end_time:
                duration = (track.end_time - track.start_time).total_seconds()
                if duration >= min_duration_seconds:
                    events.append({
                        "person_id": person.person_id,
                        "duration_seconds": duration,
                        "start_time": track.start_time.isoformat(),
                        "camera_id": track.camera_id,
                        "anomaly_score": track.anomaly_score
                    })
        
        return events
    
    @staticmethod
    def analyze_zone_activity(
        db: Session,
        zone: str,
        hours: int = 24
    ) -> Dict:
        """Analyze activity in a specific zone"""
        from backend.models.camera import Camera
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Get cameras in zone
        cameras = db.query(Camera).filter(Camera.zone == zone).all()
        camera_ids = [c.id for c in cameras]
        
        if not camera_ids:
            return {"error": "No cameras in zone"}
        
        # Count tracks
        total_tracks = db.query(Track).filter(
            Track.camera_id.in_(camera_ids),
            Track.start_time >= cutoff
        ).count()
        
        suspicious_tracks = db.query(Track).filter(
            Track.camera_id.in_(camera_ids),
            Track.start_time >= cutoff,
            Track.is_suspicious == True
        ).count()
        
        # Behavior breakdown
        behaviors = {}
        tracks = db.query(Track).filter(
            Track.camera_id.in_(camera_ids),
            Track.start_time >= cutoff
        ).all()
        
        for track in tracks:
            behavior = track.behavior_type or 'unknown'
            behaviors[behavior] = behaviors.get(behavior, 0) + 1
        
        return {
            "zone": zone,
            "time_window_hours": hours,
            "total_tracks": total_tracks,
            "suspicious_tracks": suspicious_tracks,
            "behaviors": behaviors
        }
