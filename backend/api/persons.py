# ============================================================================
# backend/api/persons.py - Person/Detection API Routes
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from backend.database import get_db
from backend.services.person_service import PersonService
from backend.services.auth_service import get_current_active_user
from backend.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/persons", tags=["Persons"])

class PersonResponse(BaseModel):
    id: int
    person_id: str
    estimated_age: Optional[int]
    estimated_gender: Optional[str]
    first_seen: datetime
    last_seen: datetime
    total_detections: int
    is_watchlisted: int
    
    class Config:
        from_attributes = True

class DetectionResponse(BaseModel):
    id: int
    person_id: int
    camera_id: int
    timestamp: datetime
    bbox: dict
    confidence: float
    emotion: Optional[str]
    is_masked: bool
    is_helmeted: bool
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[PersonResponse])
async def list_persons(
    skip: int = 0,
    limit: int = 100,
    watchlisted_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all tracked persons"""
    persons = PersonService.list_persons(db, skip, limit, watchlisted_only)
    return persons

@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get person details by ID"""
    person = PersonService.get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@router.get("/{person_id}/detections", response_model=List[DetectionResponse])
async def get_person_detections(
    person_id: str,
    camera_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all detections for a person"""
    detections = PersonService.get_person_detections(
        db, person_id, camera_id, start_time, end_time, limit
    )
    return detections

@router.get("/{person_id}/timeline")
async def get_person_timeline(
    person_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get person's movement timeline across cameras"""
    timeline = PersonService.get_person_timeline(db, person_id)
    return timeline

@router.post("/{person_id}/search-similar")
async def search_similar_persons(
    person_id: str,
    threshold: float = 0.7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Find similar persons based on appearance"""
    similar = PersonService.find_similar_persons(db, person_id, threshold)
    return {"similar_persons": similar}
