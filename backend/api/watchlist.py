# ============================================================================
# backend/api/watchlist.py - Watchlist API Routes
# ============================================================================

import datetime
import cv2
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.services.watchlist_service import WatchlistService
from backend.services.auth_service import get_current_active_user, require_admin
from backend.models.user import User
from backend.models.watchlist import WatchlistType
from pydantic import BaseModel
import numpy as np

router = APIRouter(prefix="/api/watchlist", tags=["Watchlist"])

class WatchlistEntryCreate(BaseModel):
    entry_type: WatchlistType
    synthetic_id: str
    name: str
    age: Optional[int]
    description: Optional[str]
    risk_level: Optional[str]
    last_seen_location: Optional[str]
    age_at_disappearance: Optional[int]

class WatchlistEntryResponse(BaseModel):
    id: int
    entry_type: WatchlistType
    synthetic_id: str
    name: str
    age: Optional[int]
    description: Optional[str]
    risk_level: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True

class MatchResponse(BaseModel):
    id: int
    watchlist_entry_id: int
    camera_id: int
    timestamp: datetime.datetime
    confidence: float
    similarity_score: float
    status: str
    
    class Config:
        from_attributes = True

@router.post("/", response_model=WatchlistEntryResponse)
async def create_watchlist_entry(
    entry_data: WatchlistEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create new watchlist entry (Admin only)
    
    REMINDER: Only synthetic identities allowed
    """
    entry = WatchlistService.create_entry(db, entry_data.dict())
    return entry

@router.get("/", response_model=List[WatchlistEntryResponse])
async def list_watchlist_entries(
    entry_type: Optional[WatchlistType] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List watchlist entries"""
    entries = WatchlistService.list_entries(db, entry_type, active_only)
    return entries

@router.get("/{entry_id}", response_model=WatchlistEntryResponse)
async def get_watchlist_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get watchlist entry by ID"""
    entry = WatchlistService.get_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.post("/search")
async def search_watchlist_by_image(
    file: UploadFile = File(...),
    threshold: float = 0.6,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search watchlist by uploading an image
    
    ACADEMIC USE: For testing with synthetic faces only
    """
    # Read and process image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Extract face embedding
    from backend.ml.face_recognizer import FaceRecognizer
    recognizer = FaceRecognizer()
    embedding = recognizer.get_face_embedding(image)
    
    if embedding is None:
        raise HTTPException(status_code=400, detail="No face detected in image")
    
    # Search watchlist
    matches = WatchlistService.search_watchlist(db, embedding, threshold)
    
    return {
        "matches": [
            {
                "entry": WatchlistEntryResponse.from_orm(entry),
                "similarity": float(sim)
            }
            for entry, sim in matches
        ]
    }

@router.get("/matches/recent", response_model=List[MatchResponse])
async def get_recent_matches(
    limit: int = 50,
    entry_type: Optional[WatchlistType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get recent watchlist matches"""
    from backend.models.watchlist import WatchlistMatch
    query = db.query(WatchlistMatch)
    
    if entry_type:
        from backend.models.watchlist import WatchlistEntry
        query = query.join(WatchlistEntry).filter(
            WatchlistEntry.entry_type == entry_type
        )
    
    matches = query.order_by(WatchlistMatch.timestamp.desc()).limit(limit).all()
    return matches

@router.put("/matches/{match_id}/status")
async def update_match_status(
    match_id: int,
    status: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update match status (confirm/reject)"""
    match = WatchlistService.update_match_status(
        db, match_id, status, current_user.id, notes
    )
    return match
