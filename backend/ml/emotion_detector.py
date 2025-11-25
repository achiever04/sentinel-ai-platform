# ============================================================================
# backend/ml/emotion_detector.py - Emotion Recognition
# ============================================================================

import cv2
import numpy as np
from typing import Dict, Tuple
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class EmotionDetector:
    """
    Emotion detection from facial expressions
    
    Uses classical ML with facial landmarks and geometric features.
    For better accuracy, consider fine-tuning a CNN model.
    """
    
    EMOTIONS = ['neutral', 'happy', 'sad', 'angry', 'fear', 'surprise', 'disgust']
    
    def __init__(self):
        """Initialize emotion detector"""
        logger.info("EmotionDetector initialized")
        # In production, load a trained model here
    
    def detect_emotion(
        self, 
        face_image: np.ndarray,
        landmarks: Dict = None
    ) -> Dict[str, any]:
        """
        Detect emotion from face image
        
        Args:
            face_image: Cropped face image
            landmarks: Optional facial landmarks
            
        Returns:
            Emotion detection results
        """
        if face_image.size == 0:
            return {
                'emotion': 'unknown',
                'confidence': 0.0,
                'scores': {emotion: 0.0 for emotion in self.EMOTIONS}
            }
        
        # Simplified emotion detection using geometric features
        scores = self._analyze_features(face_image, landmarks)
        
        # Get dominant emotion
        dominant_emotion = max(scores, key=scores.get)
        confidence = scores[dominant_emotion]
        
        return {
            'emotion': dominant_emotion,
            'confidence': float(confidence),
            'scores': {k: float(v) for k, v in scores.items()}
        }
    
    def _analyze_features(
        self, 
        face_image: np.ndarray, 
        landmarks: Dict = None
    ) -> Dict[str, float]:
        """
        Analyze facial features for emotion
        
        This is a simplified heuristic approach for demonstration.
        """
        # Convert to grayscale
        if len(face_image.shape) == 3:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_image
        
        h, w = gray.shape
        
        # Analyze different face regions
        upper_face = gray[:h//2, :]
        lower_face = gray[h//2:, :]
        
        # Calculate intensity statistics
        upper_mean = np.mean(upper_face)
        lower_mean = np.mean(lower_face)
        
        # Detect edges (smile, frown indicators)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        
        # Heuristic scoring (simplified)
        scores = {}
        
        # Happy: bright lower face, many edges (smile)
        scores['happy'] = (lower_mean / 255.0) * 0.6 + edge_density * 0.4
        
        # Sad: dark lower face, fewer edges
        scores['sad'] = (1 - lower_mean / 255.0) * 0.7 + (1 - edge_density) * 0.3
        
        # Angry: dark upper face (furrowed brow)
        scores['angry'] = (1 - upper_mean / 255.0) * 0.6 + edge_density * 0.4
        
        # Neutral: balanced
        balance = 1 - abs(upper_mean - lower_mean) / 128.0
        scores['neutral'] = balance * 0.7
        
        # Fear & Surprise: wide eyes (upper face bright)
        scores['fear'] = (upper_mean / 255.0) * 0.5 + edge_density * 0.5
        scores['surprise'] = (upper_mean / 255.0) * 0.6 + edge_density * 0.4
        
        # Disgust: wrinkled nose
        scores['disgust'] = edge_density * 0.6
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        
        return scores
