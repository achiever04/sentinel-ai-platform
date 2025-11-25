# ============================================================================
# scripts/test_cameras.py - Test Camera System
# ============================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from backend.processors.video_ingestor import VideoIngestor
from backend.processors.frame_processor import FrameProcessor
from backend.utils.logger import setup_logger
import time

logger = setup_logger(__name__)

def test_camera_pipeline():
    """Test complete camera processing pipeline"""
    logger.info("=== Testing Camera Pipeline ===")
    
    # Initialize components
    ingestor = VideoIngestor(source="synthetic://test", source_type="synthetic")
    processor = FrameProcessor()
    
    if not ingestor.start():
        logger.error("Failed to start video ingestor")
        return False
    
    logger.info("Video ingestor started")
    
    # Process frames
    frame_count = 0
    max_frames = 100
    
    try:
        while frame_count < max_frames:
            success, frame = ingestor.read_frame()
            
            if not success or frame is None:
                break
            
            # Process frame
            results = processor.process_frame(frame, camera_id=1, frame_id=frame_count)
            
            # Draw detections
            output_frame = processor.draw_detections(frame, results['detections'])
            
            # Display
            cv2.imshow('Camera Test', output_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            frame_count += 1
            
            if frame_count % 30 == 0:
                logger.info(f"Processed {frame_count} frames, "
                          f"Detections: {results['num_detections']}")
        
        logger.info(f"=== Test Complete: {frame_count} frames processed ===")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    finally:
        ingestor.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    success = test_camera_pipeline()
    sys.exit(0 if success else 1)