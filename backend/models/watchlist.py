# ============================================================================
# backend/models/watchlist.py - Watchlist Models
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from backend.database import Base
import enum

class WatchlistType(str, enum.Enum):
    CRIMINAL = "criminal"
    MISSING = "missing"

class WatchlistEntry(Base):
    """Synthetic watchlist entry (criminals or missing persons)"""
    __tablename__ = "watchlist_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_type = Column(SQLEnum(WatchlistType), nullable=False)
    
    # Synthetic identity
    synthetic_id = Column(String(50), unique=True, index=True)
    name = Column(String(100))  # Fictional name
    age = Column(Integer)
    description = Column(Text)
    
    # Face data
    face_images = Column(JSON)  # List of file paths
    face_embedding = Column(JSON)  # Average embedding
    
    # For missing persons
    last_seen_location = Column(String(200))
    last_seen_date = Column(DateTime(timezone=True))
    age_at_disappearance = Column(Integer)
    
    # For criminals
    risk_level = Column(String(20))  # low, medium, high, critical
    
    # Status
    is_active = Column(Integer, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WatchlistMatch(Base):
    """Match between detected person and watchlist entry"""
    __tablename__ = "watchlist_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    watchlist_entry_id = Column(Integer, ForeignKey("watchlist_entries.id"))
    person_id = Column(Integer, ForeignKey("persons.id"))
    detection_id = Column(Integer, ForeignKey("detections.id"))
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    
    # Match details
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    confidence = Column(Float)
    similarity_score = Column(Float)
    
    # Status
    status = Column(String(20), default="pending")  # pending, confirmed, rejected
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    notes = Column(Text)