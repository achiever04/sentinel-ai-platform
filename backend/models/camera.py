# ============================================================================
# backend/models/camera.py - Camera Model
# ============================================================================

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from backend.database import Base

class Camera(Base):
    """Camera/video source model"""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200))
    zone = Column(String(100))  # Logical zone (e.g., "entrance", "parking")
    source_type = Column(String(20))  # 'rtsp', 'file', 'webcam', 'synthetic'
    source_url = Column(Text)  # URL or file path
    status = Column(String(20), default="offline")  # online, offline, error
    
    # Health metrics
    fps = Column(Float, default=0.0)
    frame_count = Column(Integer, default=0)
    detection_count = Column(Integer, default=0)
    last_frame_time = Column(DateTime(timezone=True))
    
    # Configuration
    enabled = Column(Boolean, default=True)
    detection_enabled = Column(Boolean, default=True)
    recording_enabled = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
