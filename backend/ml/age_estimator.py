# ============================================================================
# backend/ml/age_estimator.py - Age Estimation & Progression
# ============================================================================

import cv2
import numpy as np
from typing import Tuple, List, Dict, Any
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class AgeEstimator:
    """
    Age estimation and age progression for synthetic missing persons
    
    ACADEMIC NOTE: Works only with synthetic faces.
    Age progression is approximate and for demonstration purposes.
    """
    
    def __init__(self):
        """Initialize age estimator"""
        logger.info("AgeEstimator initialized")
    
    def estimate_age(self, face_image: np.ndarray) -> Tuple[int, float]:
        """
        Estimate age from face image
        
        Args:
            face_image: Cropped face image
            
        Returns:
            (estimated_age, confidence)
        """
        if face_image.size == 0:
            return 0, 0.0
        
        # Simplified age estimation using facial features
        # In production, use a pre-trained deep learning model
        
        # Convert to grayscale
        if len(face_image.shape) == 3:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_image
        
        # Analyze texture (older faces have more wrinkles = higher texture)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Analyze brightness (skin tone changes with age)
        mean_brightness = np.mean(gray)
        
        # Heuristic age estimation
        texture_age = min(70, laplacian_var / 10)
        brightness_age = (1 - mean_brightness / 255) * 50
        
        estimated_age = int((texture_age + brightness_age) / 2)
        estimated_age = max(0, min(100, estimated_age + 20))  # Clamp and offset
        
        confidence = 0.6  # Low confidence for heuristic method
        
        return estimated_age, confidence
    
    def generate_age_progression(
        self,
        face_image: np.ndarray,
        current_age: int,
        target_ages: List[int]
    ) -> Dict[int, np.ndarray]:
        """
        Generate age-progressed versions of face
        
        Args:
            face_image: Current face image
            current_age: Current age
            target_ages: List of target ages to generate
            
        Returns:
            Dictionary of age -> progressed face image
        """
        progressed_faces = {}
        
        for target_age in target_ages:
            if target_age == current_age:
                progressed_faces[target_age] = face_image.copy()
            else:
                progressed = self._apply_age_transformation(
                    face_image, 
                    current_age, 
                    target_age
                )
                progressed_faces[target_age] = progressed
        
        return progressed_faces
    
    def _apply_age_transformation(
        self,
        face_image: np.ndarray,
        from_age: int,
        to_age: int
    ) -> np.ndarray:
        """
        Apply age transformation (simplified)
        
        For production, use GAN-based age progression models.
        """
        age_diff = to_age - from_age
        transformed = face_image.copy()
        
        if age_diff > 0:  # Aging
            # Darken skin slightly
            transformed = cv2.addWeighted(transformed, 1.0, transformed, -0.1, 10)
            
            # Add noise (simulate wrinkles)
            noise = np.random.normal(0, 5 * (age_diff / 10), transformed.shape)
            transformed = np.clip(transformed + noise, 0, 255).astype(np.uint8)
            
            # Slight blur (skin texture change)
            transformed = cv2.GaussianBlur(transformed, (3, 3), 0.5)
            
        else:  # De-aging
            # Brighten slightly
            transformed = cv2.addWeighted(transformed, 1.0, transformed, 0.1, 5)
            
            # Smooth skin
            transformed = cv2.bilateralFilter(transformed, 9, 75, 75)
        
        return transformed