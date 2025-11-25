# ============================================================================
# backend/ml/face_detector.py - Face Detection Module
# ============================================================================

import cv2
import numpy as np
import face_recognition
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from backend.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)

@dataclass
class FaceDetection:
    """Face detection result"""
    bbox: Tuple[int, int, int, int]  # (top, right, bottom, left)
    confidence: float
    landmarks: Optional[Dict] = None
    embedding: Optional[np.ndarray] = None

class FaceDetector:
    """
    CPU-optimized face detector using face_recognition (dlib-based)
    
    ACADEMIC NOTE: Works only with synthetic faces in this project.
    Real-world deployment requires proper consent and legal authorization.
    """
    
    def __init__(self, model: str = "hog"):
        """
        Initialize face detector
        
        Args:
            model: 'hog' (CPU, faster) or 'cnn' (more accurate, needs GPU)
        """
        self.model = model if not settings.USE_GPU else "cnn"
        self.confidence_threshold = settings.FACE_DETECTION_CONFIDENCE
        logger.info(f"FaceDetector initialized with model: {self.model}")
    
    def detect_faces(
        self, 
        image: np.ndarray,
        num_jitters: int = 1,
        extract_landmarks: bool = False
    ) -> List[FaceDetection]:
        """
        Detect faces in an image
        
        Args:
            image: Input image (BGR format from OpenCV)
            num_jitters: Number of times to re-sample for face detection (higher = more accurate)
            extract_landmarks: Whether to extract facial landmarks
            
        Returns:
            List of FaceDetection objects
        """
        # Convert BGR to RGB (face_recognition uses RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect face locations
        face_locations = face_recognition.face_locations(
            rgb_image,
            number_of_times_to_upsample=num_jitters,
            model=self.model
        )
        
        detections = []
        for face_loc in face_locations:
            top, right, bottom, left = face_loc
            
            # Calculate confidence (face_recognition doesn't provide it, so we estimate)
            # Based on face size relative to image
            face_area = (right - left) * (bottom - top)
            img_area = image.shape[0] * image.shape[1]
            confidence = min(1.0, (face_area / img_area) * 50)  # Heuristic
            
            if confidence < self.confidence_threshold:
                continue
            
            landmarks = None
            if extract_landmarks:
                landmarks = self._extract_landmarks(rgb_image, face_loc)
            
            detections.append(FaceDetection(
                bbox=(top, right, bottom, left),
                confidence=confidence,
                landmarks=landmarks
            ))
        
        logger.debug(f"Detected {len(detections)} faces")
        return detections
    
    def _extract_landmarks(self, rgb_image: np.ndarray, face_location: Tuple) -> Dict:
        """Extract facial landmarks"""
        landmarks_list = face_recognition.face_landmarks(rgb_image, [face_location])
        if landmarks_list:
            return landmarks_list[0]
        return {}
    
    def get_face_region(
        self, 
        image: np.ndarray, 
        bbox: Tuple[int, int, int, int],
        margin: float = 0.2
    ) -> np.ndarray:
        """
        Extract face region with margin
        
        Args:
            image: Input image
            bbox: Face bounding box (top, right, bottom, left)
            margin: Margin to add around face (proportion of face size)
        """
        top, right, bottom, left = bbox
        
        # Add margin
        height = bottom - top
        width = right - left
        margin_h = int(height * margin)
        margin_w = int(width * margin)
        
        top = max(0, top - margin_h)
        bottom = min(image.shape[0], bottom + margin_h)
        left = max(0, left - margin_w)
        right = min(image.shape[1], right + margin_w)
        
        return image[top:bottom, left:right]
