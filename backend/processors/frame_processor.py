# ============================================================================
# backend/processors/frame_processor.py - FIXED VERSION (No Type Errors)
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
            
            # FIXED: Store bbox as dict with INTEGER values (not tuples)
            detection = {
                'bbox': {
                    'top': int(top),
                    'right': int(right), 
                    'bottom': int(bottom),
                    'left': int(left)
                },
                'confidence': float(face_det.confidence)
            }
            
            # Step 3: Extract face embedding
            try:
                embedding = self.face_recognizer.get_face_embedding(
                    frame,
                    face_location=face_det.bbox
                )
                if embedding is not None:
                    detection['face_embedding'] = embedding.tolist()
            except Exception as e:
                logger.error(f"Error extracting embedding: {e}")
                detection['face_embedding'] = None
            
            # Step 4: Check for mask/helmet
            try:
                mask_result = self.mask_detector.detect_mask_helmet(frame, face_det.bbox)
                detection['is_masked'] = mask_result['is_masked']
                detection['is_helmeted'] = mask_result['is_helmeted']
            except Exception as e:
                logger.error(f"Error detecting mask/helmet: {e}")
                detection['is_masked'] = False
                detection['is_helmeted'] = False
            
            # Step 5: Detect emotion
            try:
                emotion_result = self.emotion_detector.detect_emotion(
                    face_region,
                    landmarks=face_det.landmarks
                )
                detection['emotion'] = emotion_result['emotion']
                detection['emotion_confidence'] = emotion_result['confidence']
            except Exception as e:
                logger.error(f"Error detecting emotion: {e}")
                detection['emotion'] = 'unknown'
                detection['emotion_confidence'] = 0.0
            
            # Step 6: Check liveness
            try:
                liveness_result = self.liveness_detector.check_liveness(face_region)
                detection['liveness_score'] = liveness_result['liveness_score']
                detection['is_spoofed'] = not liveness_result['is_live']
            except Exception as e:
                logger.error(f"Error checking liveness: {e}")
                detection['liveness_score'] = 0.5
                detection['is_spoofed'] = False
            
            detection_list.append(detection)
        
        # Step 7: Track persons across frames
        try:
            tracked_detections = self.person_tracker.update(
                camera_id,
                detection_list,
                frame_id
            )
        except Exception as e:
            logger.error(f"Error tracking persons: {e}")
            tracked_detections = detection_list
        
        # Step 8: Analyze behavior for each tracked person
        for det in tracked_detections:
            if 'person_id' in det and 'bbox' in det:
                try:
                    # FIXED: Extract bbox values properly from dict
                    bbox_dict = det['bbox']
                    bbox_tuple = (
                        bbox_dict['left'],
                        bbox_dict['top'],
                        bbox_dict['right'] - bbox_dict['left'],  # width
                        bbox_dict['bottom'] - bbox_dict['top']   # height
                    )
                    
                    behavior = self.behavior_analyzer.analyze_behavior(
                        det['person_id'],
                        bbox_tuple,
                        timestamp.timestamp()
                    )
                    det['behavior'] = behavior
                except Exception as e:
                    logger.error(f"Error analyzing behavior: {e}")
                    det['behavior'] = {
                        'activity': 'unknown',
                        'confidence': 0.0,
                        'anomaly_score': 0.0,
                        'is_suspicious': False
                    }
        
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
            try:
                # FIXED: Handle dict bbox format properly
                if isinstance(det['bbox'], dict):
                    bbox = det['bbox']
                    top = int(bbox['top'])
                    right = int(bbox['right'])
                    bottom = int(bbox['bottom'])
                    left = int(bbox['left'])
                else:
                    # Fallback for old tuple format
                    top, right, bottom, left = det['bbox']
                    top, right, bottom, left = int(top), int(right), int(bottom), int(left)
                
                # Draw bounding box
                color = (0, 255, 0)  # Green default
                if det.get('behavior', {}).get('is_suspicious', False):
                    color = (0, 0, 255)  # Red for suspicious
                
                cv2.rectangle(
                    overlay,
                    (left, top),
                    (right, bottom),
                    color,
                    2
                )
                
                # Draw person ID
                person_id = det.get('person_id', 'Unknown')
                cv2.putText(
                    overlay,
                    str(person_id),
                    (left, top - 10),
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
                        (left, bottom + 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 255, 255),
                        1
                    )
                
                # Draw mask/helmet indicators
                y_offset = top - 30
                if det.get('is_masked'):
                    cv2.putText(overlay, "MASKED", (left, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)
                if det.get('is_helmeted'):
                    cv2.putText(overlay, "HELMET", (left, y_offset - 15),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                
            except Exception as e:
                logger.error(f"Error drawing detection: {e}")
                continue
        
        return overlay