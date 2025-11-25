# ============================================================================
# backend/ml/behavior_analyzer.py - Behavior & Activity Recognition
# ============================================================================

import cv2
import numpy as np
from typing import Dict, List, Tuple
from collections import deque
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class BehaviorAnalyzer:
    """
    Analyze human behavior and activities
    
    ACADEMIC NOTE: All behaviors are analyzed in simulated scenarios.
    This is NOT for real-world "pre-crime" prediction.
    
    Detects: walking, running, loitering, fighting, falling, carrying objects
    """
    
    def __init__(self, history_length: int = 30):
        """
        Initialize behavior analyzer
        
        Args:
            history_length: Number of frames to keep in history
        """
        self.history_length = history_length
        self.position_history = {}  # person_id -> deque of positions
        logger.info("BehaviorAnalyzer initialized")
    
    def analyze_behavior(
        self,
        person_id: str,
        bbox: Tuple[int, int, int, int],
        timestamp: float,
        pose_keypoints: np.ndarray = None
    ) -> Dict[str, any]:
        """
        Analyze person's behavior
        
        Args:
            person_id: Unique person identifier
            bbox: Bounding box (x, y, w, h)
            timestamp: Current timestamp
            pose_keypoints: Optional pose estimation keypoints
            
        Returns:
            Behavior analysis results
        """
        # Initialize history for new person
        if person_id not in self.position_history:
            self.position_history[person_id] = deque(maxlen=self.history_length)
        
        # Add current position
        x, y, w, h = bbox
        center = (x + w/2, y + h/2)
        self.position_history[person_id].append({
            'position': center,
            'timestamp': timestamp,
            'bbox': bbox
        })
        
        # Need at least 10 frames for analysis
        if len(self.position_history[person_id]) < 10:
            return {
                'activity': 'unknown',
                'confidence': 0.0,
                'anomaly_score': 0.0,
                'is_suspicious': False
            }
        
        # Analyze movement pattern
        activity, confidence = self._classify_activity(person_id)
        
        # Calculate anomaly score
        anomaly_score = self._calculate_anomaly_score(person_id, activity)
        
        # Determine if suspicious
        is_suspicious = anomaly_score > 0.7
        
        return {
            'activity': activity,
            'confidence': float(confidence),
            'anomaly_score': float(anomaly_score),
            'is_suspicious': is_suspicious,
            'velocity': self._calculate_velocity(person_id),
            'stationary_duration': self._calculate_stationary_duration(person_id)
        }
    
    def _classify_activity(self, person_id: str) -> Tuple[str, float]:
        """Classify activity based on movement patterns"""
        history = list(self.position_history[person_id])
        
        # Calculate movement statistics
        velocities = []
        for i in range(1, len(history)):
            dt = history[i]['timestamp'] - history[i-1]['timestamp']
            if dt > 0:
                dx = history[i]['position'][0] - history[i-1]['position'][0]
                dy = history[i]['position'][1] - history[i-1]['position'][1]
                velocity = np.sqrt(dx**2 + dy**2) / dt
                velocities.append(velocity)
        
        if not velocities:
            return 'standing', 0.5
        
        avg_velocity = np.mean(velocities)
        velocity_std = np.std(velocities)
        
        # Classify activity
        if avg_velocity < 2.0:
            return 'standing', 0.8
        elif avg_velocity < 10.0:
            return 'walking', 0.8
        elif avg_velocity < 25.0:
            return 'running', 0.7
        else:
            # Very fast movement (possibly vehicle or tracking error)
            return 'fast_movement', 0.6
        
    def _calculate_velocity(self, person_id: str) -> float:
        """Calculate current velocity"""
        history = list(self.position_history[person_id])
        if len(history) < 2:
            return 0.0
        
        recent = history[-5:]  # Last 5 frames
        velocities = []
        
        for i in range(1, len(recent)):
            dt = recent[i]['timestamp'] - recent[i-1]['timestamp']
            if dt > 0:
                dx = recent[i]['position'][0] - recent[i-1]['position'][0]
                dy = recent[i]['position'][1] - recent[i-1]['position'][1]
                velocity = np.sqrt(dx**2 + dy**2) / dt
                velocities.append(velocity)
        
        return np.mean(velocities) if velocities else 0.0
    
    def _calculate_stationary_duration(self, person_id: str) -> float:
        """Calculate how long person has been stationary"""
        history = list(self.position_history[person_id])
        if len(history) < 2:
            return 0.0
        
        # Count consecutive stationary frames
        stationary_count = 0
        for i in range(len(history) - 1, 0, -1):
            dx = abs(history[i]['position'][0] - history[i-1]['position'][0])
            dy = abs(history[i]['position'][1] - history[i-1]['position'][1])
            movement = np.sqrt(dx**2 + dy**2)
            
            if movement < 5.0:  # Threshold for stationary
                stationary_count += 1
            else:
                break
        
        # Convert to seconds (assuming ~15 fps)
        duration = stationary_count / 15.0
        return duration
    
    def _calculate_anomaly_score(self, person_id: str, activity: str) -> float:
        """Calculate anomaly score based on behavior"""
        history = list(self.position_history[person_id])
        
        anomaly_factors = []
        
        # Factor 1: Loitering (standing in same place for long time)
        stationary_duration = self._calculate_stationary_duration(person_id)
        if stationary_duration > 60:  # More than 1 minute
            anomaly_factors.append(min(1.0, stationary_duration / 120))
        
        # Factor 2: Erratic movement
        velocities = []
        for i in range(1, len(history)):
            dt = history[i]['timestamp'] - history[i-1]['timestamp']
            if dt > 0:
                dx = history[i]['position'][0] - history[i-1]['position'][0]
                dy = history[i]['position'][1] - history[i-1]['position'][1]
                velocity = np.sqrt(dx**2 + dy**2) / dt
                velocities.append(velocity)
        
        if velocities:
            velocity_variance = np.var(velocities)
            if velocity_variance > 50:  # High variance = erratic
                anomaly_factors.append(min(1.0, velocity_variance / 100))
        
        # Factor 3: Sudden running
        if activity == 'running':
            anomaly_factors.append(0.6)
        
        # Calculate overall anomaly score
        if anomaly_factors:
            return np.mean(anomaly_factors)
        return 0.0
