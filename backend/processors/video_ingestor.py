# ============================================================================
# backend/processors/video_ingestor.py - Video Stream Ingestion
# ============================================================================

import cv2
import numpy as np
from typing import Optional, Generator, Tuple
from pathlib import Path
from backend.config import get_settings
from backend.utils.logger import setup_logger
import threading
import queue

settings = get_settings()
logger = setup_logger(__name__)

class VideoIngestor:
    """
    Ingest video from multiple sources: files, RTSP, webcam
    
    Supports:
    - Pre-recorded video files
    - RTSP streams
    - Webcam/USB cameras
    - Synthetic generated streams
    """
    
    def __init__(
        self,
        source: str,
        source_type: str = "file",
        fps: Optional[int] = None,
        resize: Optional[Tuple[int, int]] = None
    ):
        """
        Initialize video ingestor
        
        Args:
            source: Video source (file path, RTSP URL, camera index)
            source_type: 'file', 'rtsp', 'webcam', 'synthetic'
            fps: Target FPS (None for source FPS)
            resize: Resize frames to (width, height)
        """
        self.source = source
        self.source_type = source_type
        self.target_fps = fps or settings.FRAME_RATE
        self.resize = resize or (settings.FRAME_WIDTH, settings.FRAME_HEIGHT)
        
        self.cap = None
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=settings.VIDEO_BUFFER_SIZE)
        
        logger.info(f"VideoIngestor initialized for {source_type}: {source}")
    
    def start(self) -> bool:
        """Start video capture"""
        try:
            if self.source_type == "file":
                self.cap = cv2.VideoCapture(str(self.source))
            elif self.source_type == "rtsp":
                self.cap = cv2.VideoCapture(self.source)
            elif self.source_type == "webcam":
                cam_index = int(self.source) if str(self.source).isdigit() else 0
                self.cap = cv2.VideoCapture(cam_index)
            elif self.source_type == "synthetic":
                # For synthetic, we'll generate frames programmatically
                self.cap = None
            else:
                logger.error(f"Unknown source type: {self.source_type}")
                return False
            
            if self.cap is not None and not self.cap.isOpened():
                logger.error(f"Failed to open video source: {self.source}")
                return False
            
            self.is_running = True
            logger.info(f"Video capture started: {self.source}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting video capture: {e}")
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read next frame
        
        Returns:
            (success, frame) tuple
        """
        if not self.is_running:
            return False, None
        
        try:
            if self.source_type == "synthetic":
                # Generate synthetic frame
                frame = self._generate_synthetic_frame()
                return True, frame
            
            ret, frame = self.cap.read()
            
            if not ret:
                # For files, loop back to start
                if self.source_type == "file":
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.cap.read()
                
                if not ret:
                    return False, None
            
            # Resize if needed
            if self.resize:
                frame = cv2.resize(frame, self.resize)
            
            return True, frame
            
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            return False, None
    
    def _generate_synthetic_frame(self) -> np.ndarray:
        """Generate synthetic test frame"""
        # Create blank frame
        frame = np.random.randint(0, 50, (self.resize[1], self.resize[0], 3), dtype=np.uint8)
        
        # Add some synthetic "people" (colored rectangles)
        num_people = np.random.randint(1, 4)
        for _ in range(num_people):
            x = np.random.randint(0, self.resize[0] - 100)
            y = np.random.randint(0, self.resize[1] - 150)
            w, h = 80, 150
            color = tuple(np.random.randint(100, 255, 3).tolist())
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
            
            # Add "face"
            cv2.circle(frame, (x + w//2, y + 30), 20, (255, 220, 180), -1)
        
        return frame
    
    def get_fps(self) -> float:
        """Get current FPS"""
        if self.cap is not None:
            return self.cap.get(cv2.CAP_PROP_FPS)
        return self.target_fps
    
    def get_frame_count(self) -> int:
        """Get total frame count (for files)"""
        if self.cap is not None and self.source_type == "file":
            return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return 0
    
    def stop(self):
        """Stop video capture"""
        self.is_running = False
        if self.cap is not None:
            self.cap.release()
        logger.info(f"Video capture stopped: {self.source}")
