# ============================================================================
# backend/models/detection.py - Detection Model
# ============================================================================

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class Detection(Base):
    """
    Individual detection event
    
    Represents a single person detection in a frame from a camera.
    Stores face analysis, emotions, and behavioral attributes.
    """
    __tablename__ = "detections"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    person_id = Column(Integer, ForeignKey("persons.id"), index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), index=True)
    
    # Detection metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    frame_id = Column(Integer)  # Frame number in video sequence
    
    # Bounding box coordinates
    bbox = Column(JSON)  # {"top": int, "right": int, "bottom": int, "left": int}
    confidence = Column(Float)  # Detection confidence (0-1)
    
    # Face analysis
    face_detected = Column(Boolean, default=False)
    face_quality = Column(Float)  # Face image quality score (0-1)
    face_bbox = Column(JSON)  # Face-specific bounding box if different from body
    
    # Occlusion detection
    is_masked = Column(Boolean, default=False)  # Wearing face mask
    is_helmeted = Column(Boolean, default=False)  # Wearing helmet
    mask_confidence = Column(Float)  # Confidence of mask detection
    helmet_confidence = Column(Float)  # Confidence of helmet detection
    
    # Emotion recognition
    emotion = Column(String(20))  # Primary emotion: happy, sad, angry, neutral, fear, surprise, disgust
    emotion_confidence = Column(Float)  # Confidence of emotion detection
    emotion_scores = Column(JSON)  # All emotion scores as dict
    
    # Liveness & authenticity
    liveness_score = Column(Float)  # Anti-spoofing score (0-1)
    is_spoofed = Column(Boolean, default=False)  # Is this a spoof attempt?
    liveness_method = Column(String(50))  # Method used: texture, frequency, combined
    
    # Age and gender estimation
    estimated_age = Column(Integer)
    estimated_gender = Column(String(20))  # male, female, unknown
    age_confidence = Column(Float)
    gender_confidence = Column(Float)
    
    # Pose and body
    pose_landmarks = Column(JSON)  # Body keypoints from pose detection
    posture = Column(String(50))  # standing, sitting, bent_over, unknown
    
    # Frame reference
    frame_path = Column(String(500))  # Path to saved frame image (if saved)
    thumbnail_path = Column(String(500))  # Path to cropped face thumbnail
    
    # Processing metadata
    processing_time = Column(Float)  # Time taken to process this detection (seconds)
    model_version = Column(String(50))  # Version of ML models used
    
    # Relationships
    person = relationship("Person", back_populates="detections")
    camera = relationship("Camera", foreign_keys=[camera_id])
    
    def __repr__(self):
        return f"<Detection(id={self.id}, person_id={self.person_id}, camera_id={self.camera_id}, timestamp={self.timestamp})>"
    
    def to_dict(self):
        """Convert detection to dictionary"""
        return {
            "id": self.id,
            "person_id": self.person_id,
            "camera_id": self.camera_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "bbox": self.bbox,
            "confidence": self.confidence,
            "face_detected": self.face_detected,
            "face_quality": self.face_quality,
            "is_masked": self.is_masked,
            "is_helmeted": self.is_helmeted,
            "emotion": self.emotion,
            "emotion_confidence": self.emotion_confidence,
            "liveness_score": self.liveness_score,
            "is_spoofed": self.is_spoofed,
            "estimated_age": self.estimated_age,
            "estimated_gender": self.estimated_gender,
            "posture": self.posture
        }