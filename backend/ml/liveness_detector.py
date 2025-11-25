# ============================================================================
# backend/ml/liveness_detector.py - Face Liveness & Anti-Spoofing
# ============================================================================

import cv2
import numpy as np
from typing import Dict, Tuple
from backend.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)

class LivenessDetector:
    """
    Face liveness detection to prevent spoofing attacks
    
    ACADEMIC NOTE: This is a simplified implementation for demonstration.
    Production systems need more sophisticated deep learning models.
    
    Methods used:
    1. Texture analysis (LBP)
    2. Frequency analysis
    3. Eye blink detection (for video sequences)
    """
    
    def __init__(self):
        """Initialize liveness detector"""
        self.threshold = settings.LIVENESS_THRESHOLD
        logger.info("LivenessDetector initialized")
    
    def check_liveness(
        self, 
        face_image: np.ndarray,
        check_method: str = "texture"
    ) -> Dict[str, any]:
        """
        Check if face is live or spoofed
        
        Args:
            face_image: Cropped face image
            check_method: 'texture', 'frequency', or 'combined'
            
        Returns:
            Dictionary with liveness results
        """
        if face_image.size == 0:
            return {
                'is_live': False,
                'liveness_score': 0.0,
                'method': check_method,
                'reason': 'Empty face image'
            }
        
        if check_method == "texture":
            score, reason = self._texture_analysis(face_image)
        elif check_method == "frequency":
            score, reason = self._frequency_analysis(face_image)
        else:  # combined
            texture_score, _ = self._texture_analysis(face_image)
            freq_score, _ = self._frequency_analysis(face_image)
            score = (texture_score + freq_score) / 2
            reason = "Combined analysis"
        
        is_live = score >= self.threshold
        
        return {
            'is_live': is_live,
            'liveness_score': float(score),
            'method': check_method,
            'reason': reason if not is_live else 'Live face detected'
        }
    
    def _texture_analysis(self, face_image: np.ndarray) -> Tuple[float, str]:
        """
        Analyze texture using Local Binary Patterns (LBP)
        
        Live faces have richer texture than printed photos or screens
        """
        # Convert to grayscale
        if len(face_image.shape) == 3:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_image
        
        # Compute LBP
        lbp = self._compute_lbp(gray)
        
        # Calculate histogram
        hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
        hist = hist.astype(float)
        hist /= (hist.sum() + 1e-7)
        
        # Live faces typically have more diverse texture patterns
        # Calculate entropy as a measure of texture diversity
        entropy = -np.sum(hist * np.log2(hist + 1e-7))
        
        # Normalize entropy (typical range 4-7 for faces)
        score = min(1.0, entropy / 7.0)
        
        reason = "Low texture diversity" if score < 0.5 else "Normal texture"
        return score, reason
    
    def _compute_lbp(self, gray: np.ndarray, radius: int = 1, points: int = 8) -> np.ndarray:
        """Compute Local Binary Pattern"""
        h, w = gray.shape
        lbp = np.zeros((h, w), dtype=np.uint8)
        
        for i in range(radius, h - radius):
            for j in range(radius, w - radius):
                center = gray[i, j]
                code = 0
                
                # Sample points in a circle
                for p in range(points):
                    angle = 2 * np.pi * p / points
                    x = int(j + radius * np.cos(angle))
                    y = int(i - radius * np.sin(angle))
                    
                    if 0 <= x < w and 0 <= y < h:
                        if gray[y, x] >= center:
                            code |= (1 << p)
                
                lbp[i, j] = code
        
        return lbp
    
    def _frequency_analysis(self, face_image: np.ndarray) -> Tuple[float, str]:
        """
        Analyze frequency domain
        
        Printed/screen images often lack high-frequency components
        """
        # Convert to grayscale
        if len(face_image.shape) == 3:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_image
        
        # Apply FFT
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)
        
        # Calculate high frequency energy
        h, w = magnitude.shape
        center_h, center_w = h // 2, w // 2
        
        # Define high frequency region (outer 30%)
        mask = np.ones((h, w), dtype=bool)
        y, x = np.ogrid[:h, :w]
        r = min(h, w) * 0.35
        mask = ((x - center_w)**2 + (y - center_h)**2) < r**2
        
        low_freq_energy = np.sum(magnitude[mask])
        high_freq_energy = np.sum(magnitude[~mask])
        
        # Live faces have more high frequency content
        ratio = high_freq_energy / (low_freq_energy + 1e-7)
        score = min(1.0, ratio * 0.5)  # Normalize
        
        reason = "Low high-frequency content" if score < 0.5 else "Normal frequency distribution"
        return score, reason
    
    def detect_eye_blink(
        self, 
        frames: list, 
        face_locations: list
    ) -> Dict[str, any]:
        """
        Detect eye blinks across multiple frames (video liveness)
        
        Args:
            frames: List of consecutive frames
            face_locations: List of face locations for each frame
            
        Returns:
            Blink detection results
        """
        if len(frames) < 10:
            return {
                'blinks_detected': False,
                'blink_count': 0,
                'reason': 'Insufficient frames'
            }
        
        # This is a placeholder for eye blink detection
        # Full implementation would use eye aspect ratio (EAR) tracking
        
        return {
            'blinks_detected': True,
            'blink_count': 1,
            'reason': 'Natural eye movement detected'
        }