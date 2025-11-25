# ============================================================================
# backend/services/watchlist_service.py - Watchlist Management Service
# ============================================================================

import datetime
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from fastapi import HTTPException, status
from backend.models.watchlist import WatchlistEntry, WatchlistType, WatchlistMatch
from backend.ml.face_recognizer import FaceRecognizer
import numpy as np
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class WatchlistService:
    """
    Service for managing synthetic watchlists
    
    CRITICAL REMINDER: All entries are SYNTHETIC ONLY.
    Never use for real individuals without consent.
    """
    
    face_recognizer = FaceRecognizer()
    
    @staticmethod
    def create_entry(db: Session, entry_data: Dict) -> WatchlistEntry:
        """Create new watchlist entry"""
        entry = WatchlistEntry(
            entry_type=WatchlistType(entry_data['entry_type']),
            synthetic_id=entry_data['synthetic_id'],
            name=entry_data.get('name'),
            age=entry_data.get('age'),
            description=entry_data.get('description'),
            face_images=entry_data.get('face_images', []),
            face_embedding=entry_data.get('face_embedding'),
            risk_level=entry_data.get('risk_level'),
            last_seen_location=entry_data.get('last_seen_location'),
            age_at_disappearance=entry_data.get('age_at_disappearance')
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        logger.info(f"Watchlist entry created: {entry.synthetic_id}")
        return entry
    
    @staticmethod
    def get_entry(db: Session, entry_id: int) -> Optional[WatchlistEntry]:
        """Get watchlist entry by ID"""
        return db.query(WatchlistEntry).filter(WatchlistEntry.id == entry_id).first()
    
    @staticmethod
    def list_entries(
        db: Session,
        entry_type: Optional[WatchlistType] = None,
        active_only: bool = True
    ) -> List[WatchlistEntry]:
        """List watchlist entries"""
        query = db.query(WatchlistEntry)
        if entry_type:
            query = query.filter(WatchlistEntry.entry_type == entry_type)
        if active_only:
            query = query.filter(WatchlistEntry.is_active == True)
        return query.all()
    
    @staticmethod
    def search_watchlist(
        db: Session,
        face_embedding: np.ndarray,
        threshold: float = 0.6
    ) -> List[tuple]:
        """
        Search watchlist for matching faces
        
        Args:
            db: Database session
            face_embedding: Query face embedding
            threshold: Similarity threshold
            
        Returns:
            List of (WatchlistEntry, similarity_score) tuples
        """
        entries = WatchlistService.list_entries(db, active_only=True)
        matches = []
        
        for entry in entries:
            if entry.face_embedding:
                stored_embedding = np.array(entry.face_embedding)
                similarity = WatchlistService.face_recognizer.compute_similarity(
                    face_embedding,
                    stored_embedding
                )
                
                if similarity >= threshold:
                    matches.append((entry, similarity))
        
        # Sort by similarity (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    @staticmethod
    def create_match(db: Session, match_data: Dict) -> WatchlistMatch:
        """Record a watchlist match"""
        match = WatchlistMatch(
            watchlist_entry_id=match_data['watchlist_entry_id'],
            person_id=match_data.get('person_id'),
            detection_id=match_data.get('detection_id'),
            camera_id=match_data['camera_id'],
            confidence=match_data['confidence'],
            similarity_score=match_data['similarity_score']
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        return match
    
    @staticmethod
    def update_match_status(
        db: Session,
        match_id: int,
        status: str,
        user_id: int,
        notes: str = None
    ) -> WatchlistMatch:
        """Update match status (confirm/reject)"""
        match = db.query(WatchlistMatch).filter(WatchlistMatch.id == match_id).first()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        
        match.status = status
        match.reviewed_by = user_id
        match.reviewed_at = datetime.now()
        match.notes = notes
        
        db.commit()
        db.refresh(match)
        return match
