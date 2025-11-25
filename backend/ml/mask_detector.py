# ============================================================================
# backend/ml/mask_detector.py - Mask and Helmet Detection
# ============================================================================

import cv2
import numpy as np
from typing import Tuple, Dict
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class MaskHelmetDetector:
    """
    Detect face masks and helmets using classical CV techniques
    
    Note: For production, consider training a dedicated CNN model.
    This implementation uses heuristics and color/texture analysis.
    """
    
    def __init__(self):
        """Initialize mask/helmet detector"""
        # Load Haar Cascades for face and upper body
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        logger.info("MaskHelmetDetector initialized")
    
    def detect_mask_helmet(
        self, 
        image: np.ndarray, 
        face_bbox: Tuple[int, int, int, int]
    ) -> Dict[str, any]:
        """
        Detect if face is masked or wearing helmet
        
        Args:
            image: Input image
            face_bbox: Face bounding box (top, right, bottom, left)
            
        Returns:
            Dictionary with detection results
        """
        top, right, bottom, left = face_bbox
        face_region = image[top:bottom, left:right]
        
        if face_region.size == 0:
            return {
                'is_masked': False,
                'is_helmeted': False,
                'mask_confidence': 0.0,
                'helmet_confidence': 0.0
            }
        
        # Convert to grayscale
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        
        # Detect eyes
        eyes = self.eye_cascade.detectMultiScale(gray, 1.1, 5)
        has_visible_eyes = len(eyes) > 0
        
        # Calculate face region statistics
        height, width = face_region.shape[:2]
        lower_face = face_region[int(height*0.5):, :]  # Lower half of face
        
        # Mask detection heuristics
        is_masked = self._detect_mask(face_region, lower_face, has_visible_eyes)
        mask_confidence = 0.7 if is_masked else 0.3
        
        # Helmet detection heuristics
        is_helmeted = self._detect_helmet(image, face_bbox, has_visible_eyes)
        helmet_confidence = 0.7 if is_helmeted else 0.3
        
        return {
            'is_masked': is_masked,
            'is_helmeted': is_helmeted,
            'mask_confidence': mask_confidence,
            'helmet_confidence': helmet_confidence,
            'eyes_visible': has_visible_eyes
        }
    
    def _detect_mask(
        self, 
        face_region: np.ndarray, 
        lower_face: np.ndarray,
        has_visible_eyes: bool
    ) -> bool:
        """
        Detect face mask using heuristics
        
        Indicators of mask:
        - Eyes visible but mouth region covered
        - Lower face has uniform texture
        - Specific color patterns
        """
        if not has_visible_eyes:
            return False
        
        # Check lower face texture uniformity
        gray_lower = cv2.cvtColor(lower_face, cv2.COLOR_BGR2GRAY)
        texture_variance = np.var(gray_lower)
        
        # Masks typically have low texture variance
        if texture_variance < 500:  # Threshold based on experimentation
            return True
        
        # Check for typical mask colors (white, blue, black)
        hsv = cv2.cvtColor(lower_face, cv2.COLOR_BGR2HSV)
        
        # Blue mask detection
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        blue_ratio = np.count_nonzero(blue_mask) / blue_mask.size
        
        if blue_ratio > 0.3:
            return True
        
        return False
    
    def _detect_helmet(
        self, 
        image: np.ndarray, 
        face_bbox: Tuple[int, int, int, int],
        has_visible_eyes: bool
    ) -> bool:
        """
        Detect helmet/hard hat
        
        Indicators:
        - Hard edges above face region
        - Specific color patterns (yellow, white, orange)
        - Reduced face visibility
        """
        top, right, bottom, left = face_bbox
        
        # Check region above face
        if top < 20:
            return False
        
        head_region = image[max(0, top-50):top, left:right]
        
        if head_region.size == 0:
            return False
        
        # Convert to HSV
        hsv = cv2.cvtColor(head_region, cv2.COLOR_BGR2HSV)
        
        # Detect common helmet colors
        # Yellow
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        # Orange
        lower_orange = np.array([10, 100, 100])
        upper_orange = np.array([20, 255, 255])
        orange_mask = cv2.inRange(hsv, lower_orange, upper_orange)
        
        # White
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        helmet_mask = yellow_mask | orange_mask | white_mask
        helmet_ratio = np.count_nonzero(helmet_mask) / helmet_mask.size
        
        if helmet_ratio > 0.25:
            return True
        
        # Check for reduced face visibility
        if not has_visible_eyes:
            # Detect hard edges in head region
            gray = cv2.cvtColor(head_region, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_ratio = np.count_nonzero(edges) / edges.size
            
            if edge_ratio > 0.15:
                return True
        
        return False