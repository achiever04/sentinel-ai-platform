# ============================================================================
# backend/tasks/video_tasks.py - Video Processing Tasks
# ============================================================================

from backend.tasks.celery_app import celery_app
from backend.utils.logger import setup_logger
import cv2

logger = setup_logger(__name__)

@celery_app.task(name='process_uploaded_video')
def process_uploaded_video(video_path: str, camera_id: int = None):
    """Process uploaded video file"""
    logger.info(f"Processing video: {video_path}")
    
    try:
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        detections_count = 0
        
        from backend.processors.frame_processor import FrameProcessor
        processor = FrameProcessor()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every 5th frame for efficiency
            if frame_count % 5 == 0:
                results = processor.process_frame(
                    frame,
                    camera_id or 0,
                    frame_count
                )
                detections_count += results['num_detections']
            
            frame_count += 1
        
        cap.release()
        
        logger.info(f"Processed {frame_count} frames, found {detections_count} detections")
        
        return {
            'status': 'completed',
            'frames_processed': frame_count,
            'total_detections': detections_count
        }
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }