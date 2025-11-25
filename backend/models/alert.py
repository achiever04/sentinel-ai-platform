# ============================================================================
# backend/models/alert.py - Alert Model
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.sql import func
from backend.database import Base

class Alert(Base):
    """System alert/notification"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50))  # watchlist_match, suspicious_behavior, camera_health, etc.
    severity = Column(String(20))  # info, warning, critical
    
    # Related entities
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    person_id = Column(Integer, ForeignKey("persons.id"))
    detection_id = Column(Integer, ForeignKey("detections.id"))
    watchlist_match_id = Column(Integer, ForeignKey("watchlist_matches.id"))
    
    # Alert content
    title = Column(String(200))
    message = Column(Text)
    alert_metadata = Column(JSON)  # Additional context
    
    # Status
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime(timezone=True))
    
    # Delivery status
    voice_alert_sent = Column(Boolean, default=False)
    email_alert_sent = Column(Boolean, default=False)
