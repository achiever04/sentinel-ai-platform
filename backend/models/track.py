# ============================================================================
# backend/models/track.py - Track Model
# ============================================================================

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
from datetime import datetime

class Track(Base):
    """
    Movement track of a person within or across cameras
    
    Represents continuous movement/presence of a person over time.
    Used for behavioral analysis and pattern detection.
    """
    __tablename__ = "tracks"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    person_id = Column(Integer, ForeignKey("persons.id"), index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), index=True)
    
    # Track timing
    start_time = Column(DateTime(timezone=True), index=True)
    end_time = Column(DateTime(timezone=True))
    duration = Column(Float)  # Duration in seconds
    
    # Movement path
    path = Column(JSON)  # List of positions: [{"x": float, "y": float, "t": timestamp}, ...]
    path_length = Column(Float)  # Total distance traveled (pixels or meters)
    
    # Velocity and motion
    average_velocity = Column(Float)  # Average speed
    max_velocity = Column(Float)  # Maximum speed
    velocity_variance = Column(Float)  # Variance in velocity (erratic movement indicator)
    
    # Behavior classification
    behavior_type = Column(String(50))  # walking, running, standing, loitering, etc.
    behavior_confidence = Column(Float)  # Confidence of behavior classification
    
    # Anomaly detection
    anomaly_score = Column(Float, default=0.0)  # Overall anomaly score (0-1)
    is_suspicious = Column(Boolean, default=False)  # Flagged as suspicious
    anomaly_reasons = Column(JSON)  # List of reasons for anomaly: ["loitering", "erratic_movement"]
    
    # Activity details
    stationary_duration = Column(Float)  # Time spent stationary (seconds)
    direction = Column(String(50))  # General direction: north, south, east, west, stationary
    zone_transitions = Column(JSON)  # List of zone changes: [{"from": "entrance", "to": "corridor", "time": ...}]
    
    # Interaction detection
    interactions = Column(JSON)  # Interactions with other persons: [{"person_id": int, "type": "approach", "time": ...}]
    object_interactions = Column(JSON)  # Interactions with objects: [{"object": "door", "action": "open", "time": ...}]
    
    # Pose and posture over time
    primary_posture = Column(String(50))  # Most common posture during track
    posture_changes = Column(Integer)  # Number of posture changes
    
    # Emotion tracking
    dominant_emotion = Column(String(20))  # Most common emotion during track
    emotion_changes = Column(JSON)  # Significant emotion changes: [{"from": "neutral", "to": "angry", "time": ...}]
    
    # Risk assessment
    risk_level = Column(String(20))  # low, medium, high, critical
    risk_factors = Column(JSON)  # Factors contributing to risk score
    
    # Alert generation
    alert_triggered = Column(Boolean, default=False)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    alert_reason = Column(Text)
    
    # Track quality metrics
    detection_count = Column(Integer, default=0)  # Number of detections in this track
    tracking_confidence = Column(Float)  # Overall tracking quality
    occlusion_count = Column(Integer, default=0)  # Times person was occluded
    
    # Entry/exit points
    entry_point = Column(JSON)  # Where person entered: {"x": float, "y": float, "zone": "entrance"}
    exit_point = Column(JSON)  # Where person exited: {"x": float, "y": float, "zone": "exit"}
    
    # Cross-camera tracking
    previous_track_id = Column(Integer, ForeignKey("tracks.id"))  # Previous track (different camera)
    next_track_id = Column(Integer, ForeignKey("tracks.id"))  # Next track (different camera)
    is_cross_camera = Column(Boolean, default=False)  # Part of multi-camera track
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Notes and annotations
    notes = Column(Text)  # Operator notes
    reviewed = Column(Boolean, default=False)  # Has been reviewed by operator
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    
    # Relationships
    person = relationship("Person", back_populates="tracks", foreign_keys=[person_id])
    camera = relationship("Camera", foreign_keys=[camera_id])
    alert = relationship("Alert", foreign_keys=[alert_id])
    
    # Self-referential relationships for track chains
    previous_track = relationship("Track", remote_side=[id], foreign_keys=[previous_track_id])
    next_track = relationship("Track", remote_side=[id], foreign_keys=[next_track_id])
    
    def __repr__(self):
        return f"<Track(id={self.id}, person_id={self.person_id}, behavior={self.behavior_type}, suspicious={self.is_suspicious})>"
    
    def calculate_duration(self):
        """Calculate track duration if not set"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration = delta.total_seconds()
        return self.duration
    
    def add_position(self, x: float, y: float, timestamp: datetime = None):
        """Add a position to the track path"""
        if self.path is None:
            self.path = []
        
        if timestamp is None:
            timestamp = datetime.now()
        
        self.path.append({
            "x": x,
            "y": y,
            "t": timestamp.isoformat()
        })
    
    def get_trajectory(self):
        """Get trajectory as list of (x, y) tuples"""
        if not self.path:
            return []
        return [(p["x"], p["y"]) for p in self.path]
    
    def is_loitering(self, threshold_seconds: float = 60) -> bool:
        """Check if track indicates loitering"""
        if self.stationary_duration and self.stationary_duration > threshold_seconds:
            return True
        if self.behavior_type == "loitering":
            return True
        return False
    
    def to_dict(self):
        """Convert track to dictionary"""
        return {
            "id": self.id,
            "person_id": self.person_id,
            "camera_id": self.camera_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "behavior_type": self.behavior_type,
            "anomaly_score": self.anomaly_score,
            "is_suspicious": self.is_suspicious,
            "risk_level": self.risk_level,
            "average_velocity": self.average_velocity,
            "stationary_duration": self.stationary_duration,
            "detection_count": self.detection_count,
            "path_length": len(self.path) if self.path else 0
        }