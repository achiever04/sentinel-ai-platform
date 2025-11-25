# ============================================================================
# backend/ml/pose_detector.py - Pose Detection Module
# ============================================================================

import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Optional
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class PoseDetector:
    """
    Pose detection using MediaPipe (CPU-optimized)
    
    Detects human body keypoints for activity recognition
    """
    
    def __init__(self):
        """Initialize pose detector"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # Lightest model for CPU
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        logger.info("PoseDetector initialized with MediaPipe")
    
    def detect_pose(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect pose keypoints in image
        
        Args:
            image: Input image (BGR)
            
        Returns:
            Dictionary with pose landmarks and visibility
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process image
        results = self.pose.process(rgb_image)
        
        if not results.pose_landmarks:
            return None
        
        # Extract keypoints
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            })
        
        return {
            'landmarks': landmarks,
            'has_pose': True
        }
    
    def get_pose_angles(self, landmarks: List[Dict]) -> Dict[str, float]:
        """Calculate important joint angles"""
        if len(landmarks) < 33:  # MediaPipe has 33 landmarks
            return {}
        
        angles = {}
        
        # Helper function to calculate angle
        def calculate_angle(p1, p2, p3):
            """Calculate angle between three points"""
            v1 = np.array([p1['x'] - p2['x'], p1['y'] - p2['y']])
            v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y']])
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
            return np.degrees(angle)
        
        # Left elbow angle
        if all(landmarks[i]['visibility'] > 0.5 for i in [11, 13, 15]):
            angles['left_elbow'] = calculate_angle(
                landmarks[11],  # left shoulder
                landmarks[13],  # left elbow
                landmarks[15]   # left wrist
            )
        
        # Right elbow angle
        if all(landmarks[i]['visibility'] > 0.5 for i in [12, 14, 16]):
            angles['right_elbow'] = calculate_angle(
                landmarks[12],  # right shoulder
                landmarks[14],  # right elbow
                landmarks[16]   # right wrist
            )
        
        # Left knee angle
        if all(landmarks[i]['visibility'] > 0.5 for i in [23, 25, 27]):
            angles['left_knee'] = calculate_angle(
                landmarks[23],  # left hip
                landmarks[25],  # left knee
                landmarks[27]   # left ankle
            )
        
        # Right knee angle
        if all(landmarks[i]['visibility'] > 0.5 for i in [24, 26, 28]):
            angles['right_knee'] = calculate_angle(
                landmarks[24],  # right hip
                landmarks[26],  # right knee
                landmarks[28]   # right ankle
            )
        
        return angles
    
    def classify_posture(self, landmarks: List[Dict]) -> str:
        """Classify body posture"""
        if not landmarks or len(landmarks) < 33:
            return 'unknown'
        
        # Get key landmarks
        nose = landmarks[0]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        
        # Check visibility
        if min(nose['visibility'], left_shoulder['visibility'], 
               right_shoulder['visibility']) < 0.5:
            return 'unknown'
        
        # Calculate body orientation
        shoulder_center_y = (left_shoulder['y'] + right_shoulder['y']) / 2
        hip_center_y = (left_hip['y'] + right_hip['y']) / 2
        
        # Standing: shoulders significantly above hips
        if shoulder_center_y < hip_center_y - 0.15:
            return 'standing'
        
        # Sitting/crouching: shoulders close to hips
        elif abs(shoulder_center_y - hip_center_y) < 0.1:
            return 'sitting'
        
        # Bent over
        elif shoulder_center_y > hip_center_y:
            return 'bent_over'
        
        return 'standing'
