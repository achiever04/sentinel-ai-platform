# ============================================================================
# backend/processors/frame_processor.py - Frame Processing Pipeline
# ============================================================================

import cv2
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from backend.ml.face_detector import FaceDetector
from backend.ml.face_recognizer import FaceRecognizer
from backend.ml.mask_detector import MaskHelmetDetector
from backend.ml.emotion_detector import EmotionDetector
from backend.ml.liveness_detector import LivenessDetector
from backend.ml.behavior_analyzer import BehaviorAnalyzer
from backend.ml.person_tracker import PersonTracker
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class FrameProcessor:
    """
    Process video frames through complete ML pipeline
    
    Pipeline:
    1. Face detection
    2. Face recognition (embedding extraction)
    3. Mask/helmet detection
    4. Emotion detection
    5. Liveness check
    6. Person tracking
    7. Behavior analysis
    """
    
    def __init__(self):
        """Initialize frame processor with all ML components"""
        self.face_detector = FaceDetector()
        self.face_recognizer = FaceRecognizer()
        self.mask_detector = MaskHelmetDetector()
        self.emotion_detector = EmotionDetector()
        self.liveness_detector = LivenessDetector()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.person_tracker = PersonTracker()
        
        logger.info("FrameProcessor initialized with full ML pipeline")
    
    def process_frame(
        self,
        frame: np.ndarray,
        camera_id: int,
        frame_id: int,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Process single frame through complete pipeline
        
        Args:
            frame: Input frame (BGR)
            camera_id: Camera identifier
            frame_id: Frame number
            timestamp: Frame timestamp
            
        Returns:
            Processing results dictionary
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        results = {
            'camera_id': camera_id,
            'frame_id': frame_id,
            'timestamp': timestamp,
            'detections': [],
            'frame_shape': frame.shape
        }
        
        # Step 1: Detect faces
        face_detections = self.face_detector.detect_faces(frame, extract_landmarks=True)
        
        if not face_detections:
            return results
        
        # Step 2: Process each detected face
        detection_list = []
        
        for face_det in face_detections:
            top, right, bottom, left = face_det.bbox
            face_region = frame[top:bottom, left:right]
            
            if face_region.size == 0:
                continue
            
            detection = {
                'bbox': {'top': top, 'right': right, 'bottom': bottom, 'left': left},
                'confidence': face_det.confidence
            }
            
            # Step 3: Extract face embedding
            embedding = self.face_recognizer.get_face_embedding(
                frame,
                face_location=face_det.bbox
            )
            if embedding is not None:
                detection['face_embedding'] = embedding.tolist()
            
            # Step 4: Check for mask/helmet
            mask_result = self.mask_detector.detect_mask_helmet(frame, face_det.bbox)
            detection['is_masked'] = mask_result['is_masked']
            detection['is_helmeted'] = mask_result['is_helmeted']
            
            # Step 5: Detect emotion
            emotion_result = self.emotion_detector.detect_emotion(
                face_region,
                landmarks=face_det.landmarks
            )
            detection['emotion'] = emotion_result['emotion']
            detection['emotion_confidence'] = emotion_result['confidence']
            
            # Step 6: Check liveness
            liveness_result = self.liveness_detector.check_liveness(face_region)
            detection['liveness_score'] = liveness_result['liveness_score']
            detection['is_spoofed'] = not liveness_result['is_live']
            
            detection_list.append(detection)
        
        # Step 7: Track persons across frames
        tracked_detections = self.person_tracker.update(
            camera_id,
            detection_list,
            frame_id
        )
        
        # Step 8: Analyze behavior for each tracked person
        for det in tracked_detections:
            if 'person_id' in det:
                behavior = self.behavior_analyzer.analyze_behavior(
                    det['person_id'],
                    (det['bbox']['left'], det['bbox']['top'],
                     det['bbox']['right'] - det['bbox']['left'],
                     det['bbox']['bottom'] - det['bbox']['top']),
                    timestamp.timestamp()
                )
                det['behavior'] = behavior
        
        results['detections'] = tracked_detections
        results['num_detections'] = len(tracked_detections)
        
        return results
    
    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Dict]
    ) -> np.ndarray:
        """
        Draw detection overlays on frame
        
        Args:
            frame: Input frame
            detections: List of detection dictionaries
            
        Returns:
            Frame with overlays
        """
        overlay = frame.copy()
        
        for det in detections:
            bbox = det['bbox']
            
            # Draw bounding box
            color = (0, 255, 0)  # Green default
            if det.get('behavior', {}).get('is_suspicious', False):
                color = (0, 0, 255)  # Red for suspicious
            
            cv2.rectangle(
                overlay,
                (bbox['left'], bbox['top']),
                (bbox['right'], bbox['bottom']),
                color,
                2
            )
            
            # Draw person ID
            person_id = det.get('person_id', 'Unknown')
            cv2.putText(
                overlay,
                person_id,
                (bbox['left'], bbox['top'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )
            
            # Draw emotion
            emotion = det.get('emotion', '')
            if emotion:
                cv2.putText(
                    overlay,
                    emotion,
                    (bbox['left'], bbox['bottom'] + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 255, 255),
                    1
                )
            
            # Draw mask/helmet indicators
            y_offset = bbox['top'] - 30
            if det.get('is_masked'):
                cv2.putText(overlay, "MASKED", (bbox['left'], y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)
            if det.get('is_helmeted'):
                cv2.putText(overlay, "HELMET", (bbox['left'], y_offset - 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        return overlay