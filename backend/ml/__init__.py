# ============================================================================
# backend/ml/__init__.py
# ============================================================================

"""
Machine Learning Models Package

All ML/AI components for computer vision and analysis
CPU-optimized for efficient processing on limited hardware
"""

from backend.ml.face_detector import FaceDetector, FaceDetection
from backend.ml.face_recognizer import FaceRecognizer
from backend.ml.person_tracker import PersonTracker
from backend.ml.mask_detector import MaskHelmetDetector
from backend.ml.liveness_detector import LivenessDetector
from backend.ml.emotion_detector import EmotionDetector
from backend.ml.behavior_analyzer import BehaviorAnalyzer
from backend.ml.age_estimator import AgeEstimator
from backend.ml.pose_detector import PoseDetector
from backend.ml.deepfake_detector import DeepfakeDetector
from backend.ml.federated_learner import FederatedLearner

__all__ = [
    # Face analysis
    "FaceDetector",
    "FaceDetection",
    "FaceRecognizer",
    "MaskHelmetDetector",
    
    # Liveness and authenticity
    "LivenessDetector",
    "DeepfakeDetector",
    
    # Behavioral analysis
    "EmotionDetector",
    "BehaviorAnalyzer",
    "PoseDetector",
    
    # Person tracking
    "PersonTracker",
    
    # Age analysis
    "AgeEstimator",
    
    # Federated learning
    "FederatedLearner",
]