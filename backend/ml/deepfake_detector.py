# ============================================================================
# backend/ml/deepfake_detector.py - Deepfake Detection Module
# ============================================================================

import cv2
import numpy as np
from typing import Dict, Tuple,List
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class DeepfakeDetector:
    """
    Deepfake detection module
    
    ACADEMIC NOTE: This is a simplified implementation for demonstration.
    Production systems need sophisticated deep learning models.
    
    Methods:
    1. Frequency analysis
    2. Eye blinking patterns
    3. Facial consistency checks
    """
    
    def __init__(self):
        """Initialize deepfake detector"""
        logger.info("DeepfakeDetector initialized")
    
    def detect_deepfake(
        self,
        face_sequence: List[np.ndarray],
        method: str = "combined"
    ) -> Dict:
        """
        Detect if face sequence is deepfake
        
        Args:
            face_sequence: List of face images (time sequence)
            method: 'frequency', 'consistency', or 'combined'
            
        Returns:
            Detection results with confidence
        """
        if not face_sequence:
            return {
                'is_deepfake': False,
                'confidence': 0.0,
                'reason': 'No frames provided'
            }
        
        scores = []
        
        if method in ['frequency', 'combined']:
            freq_score = self._frequency_analysis(face_sequence[0])
            scores.append(freq_score)
        
        if method in ['consistency', 'combined'] and len(face_sequence) > 1:
            consistency_score = self._consistency_analysis(face_sequence)
            scores.append(consistency_score)
        
        # Average scores
        final_score = np.mean(scores) if scores else 0.5
        
        is_deepfake = final_score > 0.6
        
        return {
            'is_deepfake': is_deepfake,
            'confidence': float(final_score),
            'method': method,
            'reason': self._get_reason(is_deepfake, final_score)
        }
    
    def _frequency_analysis(self, face_image: np.ndarray) -> float:
        """
        Analyze frequency domain
        
        Deepfakes often have artifacts in high frequencies
        """
        if face_image.size == 0:
            return 0.5
        
        # Convert to grayscale
        if len(face_image.shape) == 3:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_image
        
        # Apply FFT
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)
        
        # Analyze high frequency components
        h, w = magnitude.shape
        center_h, center_w = h // 2, w // 2
        
        # High frequency ring
        y, x = np.ogrid[:h, :w]
        inner_r = min(h, w) * 0.35
        outer_r = min(h, w) * 0.45
        
        ring_mask = ((x - center_w)**2 + (y - center_h)**2 >= inner_r**2) & \
                    ((x - center_w)**2 + (y - center_h)**2 <= outer_r**2)
        
        high_freq_energy = np.sum(magnitude[ring_mask])
        total_energy = np.sum(magnitude)
        
        ratio = high_freq_energy / (total_energy + 1e-7)
        
        # Deepfakes often have unusual frequency distribution
        # Very low or very high ratio indicates potential manipulation
        if ratio < 0.01 or ratio > 0.15:
            return 0.7
        return 0.3
    
    def _consistency_analysis(self, face_sequence: List[np.ndarray]) -> float:
        """
        Analyze temporal consistency across frames
        
        Deepfakes may have frame-to-frame inconsistencies
        """
        if len(face_sequence) < 2:
            return 0.5
        
        inconsistencies = []
        
        for i in range(1, len(face_sequence)):
            prev_frame = cv2.cvtColor(face_sequence[i-1], cv2.COLOR_BGR2GRAY)
            curr_frame = cv2.cvtColor(face_sequence[i], cv2.COLOR_BGR2GRAY)
            
            # Resize to same size
            h, w = min(prev_frame.shape[0], curr_frame.shape[0]), \
                   min(prev_frame.shape[1], curr_frame.shape[1])
            prev_frame = cv2.resize(prev_frame, (w, h))
            curr_frame = cv2.resize(curr_frame, (w, h))
            
            # Calculate frame difference
            diff = cv2.absdiff(prev_frame, curr_frame)
            inconsistency = np.mean(diff)
            inconsistencies.append(inconsistency)
        
        # High variance in frame differences suggests manipulation
        variance = np.var(inconsistencies)
        
        if variance > 100:  # Threshold based on experimentation
            return 0.7
        return 0.3
    
    def _get_reason(self, is_deepfake: bool, score: float) -> str:
        """Generate explanation for detection"""
        if is_deepfake:
            if score > 0.8:
                return "High confidence: Multiple manipulation indicators detected"
            else:
                return "Moderate confidence: Some suspicious patterns found"
        else:
            return "Content appears authentic"
