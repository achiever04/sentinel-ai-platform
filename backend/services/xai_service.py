# ============================================================================
# backend/services/xai_service.py - Explainable AI Service
# ============================================================================

from typing import Dict, List
import numpy as np
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class XAIService:
    """
    Service for providing explainable AI insights
    
    Provides transparency on model decisions for user trust
    """
    
    @staticmethod
    def explain_face_match(
        similarity_score: float,
        threshold: float,
        face_quality: float,
        alternative_matches: List[tuple] = None
    ) -> Dict:
        """
        Explain why a face match was made or rejected
        
        Args:
            similarity_score: Similarity between faces (0-1)
            threshold: Matching threshold
            face_quality: Quality score of detected face
            alternative_matches: List of (name, score) alternatives
        """
        is_match = similarity_score >= threshold
        confidence = similarity_score
        
        explanation_parts = []
        
        # Main decision
        if is_match:
            explanation_parts.append(
                f"Match confirmed: similarity score {similarity_score:.3f} "
                f"exceeds threshold {threshold:.3f}"
            )
        else:
            explanation_parts.append(
                f"No match: similarity score {similarity_score:.3f} "
                f"below threshold {threshold:.3f}"
            )
        
        # Face quality factor
        if face_quality < 0.5:
            explanation_parts.append(
                f"Note: Low face quality ({face_quality:.2f}) may affect accuracy"
            )
            confidence *= 0.8  # Reduce confidence for low quality
        
        # Alternative matches
        if alternative_matches:
            top_alt = alternative_matches[0]
            explanation_parts.append(
                f"Next closest match: {top_alt[0]} with score {top_alt[1]:.3f}"
            )
        
        return {
            "decision": "match" if is_match else "no_match",
            "confidence": float(confidence),
            "similarity_score": float(similarity_score),
            "threshold": float(threshold),
            "face_quality": float(face_quality),
            "explanation": " | ".join(explanation_parts),
            "alternative_matches": alternative_matches[:3] if alternative_matches else []
        }
    
    @staticmethod
    def explain_behavior_classification(
        activity: str,
        anomaly_score: float,
        velocity: float,
        stationary_duration: float,
        features: Dict = None
    ) -> Dict:
        """Explain behavior classification decision"""
        is_suspicious = anomaly_score > 0.7
        
        explanation_parts = []
        
        # Activity classification
        explanation_parts.append(f"Detected activity: {activity}")
        
        # Anomaly factors
        if anomaly_score > 0.7:
            explanation_parts.append(
                f"High anomaly score ({anomaly_score:.2f}) - flagged as suspicious"
            )
            
            if stationary_duration > 60:
                explanation_parts.append(
                    f"Loitering detected: stationary for {stationary_duration:.0f} seconds"
                )
            
            if velocity > 20:
                explanation_parts.append(
                    f"Unusual speed detected: {velocity:.1f} pixels/second"
                )
        else:
            explanation_parts.append(
                f"Normal behavior: anomaly score {anomaly_score:.2f}"
            )
        
        # Feature importance
        feature_importance = {}
        if stationary_duration > 30:
            feature_importance['stationary_duration'] = 0.6
        if velocity > 15:
            feature_importance['velocity'] = 0.4
        
        return {
            "activity": activity,
            "is_suspicious": is_suspicious,
            "anomaly_score": float(anomaly_score),
            "confidence": 0.8,  # Behavior analysis confidence
            "explanation": " | ".join(explanation_parts),
            "key_features": {
                "velocity": float(velocity),
                "stationary_duration": float(stationary_duration)
            },
            "feature_importance": feature_importance
        }
    
    @staticmethod
    def explain_emotion_detection(
        emotion: str,
        confidence: float,
        emotion_scores: Dict[str, float]
    ) -> Dict:
        """Explain emotion detection result"""
        # Sort emotions by score
        sorted_emotions = sorted(
            emotion_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        explanation_parts = [
            f"Primary emotion: {emotion} (confidence: {confidence:.2f})"
        ]
        
        # Show runner-up emotions
        if len(sorted_emotions) > 1:
            runner_up = sorted_emotions[1]
            explanation_parts.append(
                f"Secondary: {runner_up[0]} ({runner_up[1]:.2f})"
            )
        
        # Confidence warning
        if confidence < 0.5:
            explanation_parts.append(
                "Low confidence - result may be unreliable"
            )
        
        return {
            "emotion": emotion,
            "confidence": float(confidence),
            "explanation": " | ".join(explanation_parts),
            "all_emotions": {k: float(v) for k, v in sorted_emotions},
            "top_3_emotions": [
                {"emotion": k, "score": float(v)}
                for k, v in sorted_emotions[:3]
            ]
        }
    
    @staticmethod
    def explain_liveness_detection(
        is_live: bool,
        liveness_score: float,
        method: str,
        reason: str
    ) -> Dict:
        """Explain liveness detection result"""
        explanation_parts = []
        
        if is_live:
            explanation_parts.append(
                f"Live face detected (score: {liveness_score:.2f})"
            )
        else:
            explanation_parts.append(
                f"Possible spoof detected (score: {liveness_score:.2f})"
            )
            explanation_parts.append(f"Reason: {reason}")
        
        explanation_parts.append(f"Detection method: {method}")
        
        return {
            "is_live": is_live,
            "liveness_score": float(liveness_score),
            "method": method,
            "explanation": " | ".join(explanation_parts),
            "recommendation": (
                "Face appears genuine" if is_live
                else "Verify with additional authentication"
            )
        }
