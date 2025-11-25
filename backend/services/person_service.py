# ============================================================================
# backend/services/person_service.py - Person Management Service
# ============================================================================

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.models.person import Person
from backend.models.camera import Camera
from backend.models.detection import Detection
from backend.models.track import Track
from backend.utils.logger import setup_logger
import numpy as np

logger = setup_logger(__name__)

class PersonService:
    """Service for managing tracked persons and detections"""
    
    @staticmethod
    def list_persons(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        watchlisted_only: bool = False
    ) -> List[Person]:
        """List all tracked persons"""
        query = db.query(Person)
        
        if watchlisted_only:
            query = query.filter(Person.is_watchlisted > 0)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_person_by_id(db: Session, person_id: str) -> Optional[Person]:
        """Get person by person_id string (e.g., 'Person_0001')"""
        return db.query(Person).filter(Person.person_id == person_id).first()
    
    @staticmethod
    def get_person_detections(
        db: Session,
        person_id: str,
        camera_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Detection]:
        """Get all detections for a person"""
        person = PersonService.get_person_by_id(db, person_id)
        if not person:
            return []
        
        query = db.query(Detection).filter(Detection.person_id == person.id)
        
        if camera_id:
            query = query.filter(Detection.camera_id == camera_id)
        if start_time:
            query = query.filter(Detection.timestamp >= start_time)
        if end_time:
            query = query.filter(Detection.timestamp <= end_time)
        
        return query.order_by(Detection.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_person_timeline(db: Session, person_id: str) -> dict:
        """Get person's movement timeline across cameras"""
        person = PersonService.get_person_by_id(db, person_id)
        if not person:
            return {"error": "Person not found"}
        
        # Get all detections with camera info
        detections = db.query(Detection, Camera).join(
            Camera, Detection.camera_id == Camera.id
        ).filter(
            Detection.person_id == person.id
        ).order_by(Detection.timestamp).all()
        
        timeline = []
        for detection, camera in detections:
            timeline.append({
                "timestamp": detection.timestamp.isoformat(),
                "camera_id": camera.id,
                "camera_name": camera.name,
                "location": camera.location,
                "zone": camera.zone,
                "emotion": detection.emotion,
                "is_masked": detection.is_masked
            })
        
        return {
            "person_id": person_id,
            "first_seen": person.first_seen.isoformat(),
            "last_seen": person.last_seen.isoformat(),
            "total_appearances": len(timeline),
            "timeline": timeline
        }
    
    @staticmethod
    def find_similar_persons(
        db: Session,
        person_id: str,
        threshold: float = 0.7
    ) -> List[dict]:
        """Find similar persons based on appearance embedding"""
        person = PersonService.get_person_by_id(db, person_id)
        if not person or not person.face_embedding:
            return []
        
        query_embedding = np.array(person.face_embedding)
        all_persons = db.query(Person).filter(Person.person_id != person_id).all()
        
        similar = []
        for other in all_persons:
            if other.face_embedding:
                other_embedding = np.array(other.face_embedding)
                
                # Compute cosine similarity
                similarity = np.dot(query_embedding, other_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(other_embedding)
                )
                
                if similarity >= threshold:
                    similar.append({
                        "person_id": other.person_id,
                        "similarity": float(similarity),
                        "first_seen": other.first_seen.isoformat(),
                        "last_seen": other.last_seen.isoformat()
                    })
        
        # Sort by similarity
        similar.sort(key=lambda x: x['similarity'], reverse=True)
        return similar
    
    @staticmethod
    def create_person(db: Session, person_data: dict) -> Person:
        """Create new person entry"""
        person = Person(**person_data)
        db.add(person)
        db.commit()
        db.refresh(person)
        return person
    
    @staticmethod
    def update_person(db: Session, person_id: str, update_data: dict) -> Person:
        """Update person details"""
        person = PersonService.get_person_by_id(db, person_id)
        if not person:
            return None
        
        for key, value in update_data.items():
            if hasattr(person, key):
                setattr(person, key, value)
        
        db.commit()
        db.refresh(person)
        return person
