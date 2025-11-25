from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class Person(Base):
    """Anonymized person entity tracked across cameras"""
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String(50), unique=True, index=True)
    
    # Appearance features
    face_embedding = Column(JSON)
    body_embedding = Column(JSON)
    
    # Attributes
    estimated_age = Column(Integer)
    estimated_gender = Column(String(20))
    dominant_clothing_color = Column(String(50))
    
    # Status
    is_watchlisted = Column(Integer, default=0)
    watchlist_confidence = Column(Float)
    
    # Tracking
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True))
    total_detections = Column(Integer, default=0)
    
    # Relationships - Import from separate files
    detections = relationship("Detection", back_populates="person")
    tracks = relationship("Track", back_populates="person")

# Detection and Track classes are now in separate files:
# - backend/models/detection.py
# - backend/models/track.py