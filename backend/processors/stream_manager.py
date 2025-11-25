# ============================================================================
# backend/processors/stream_manager.py - Multi-Stream Manager
# ============================================================================

import threading
import queue
from typing import Dict, List, Optional
from backend.processors.video_ingestor import VideoIngestor
from backend.processors.frame_processor import FrameProcessor
from backend.utils.logger import setup_logger
from backend.config import get_settings
import time

settings = get_settings()
logger = setup_logger(__name__)

class StreamManager:
    """
    Manage multiple video streams simultaneously
    
    Coordinates ingestion, processing, and distribution of frames
    """
    
    def __init__(self, max_streams: int = None):
        """Initialize stream manager"""
        self.max_streams = max_streams or settings.MAX_CAMERA_FEEDS
        self.streams: Dict[int, VideoIngestor] = {}
        self.processors: Dict[int, threading.Thread] = {}
        self.frame_queues: Dict[int, queue.Queue] = {}
        self.running = False
        
        self.frame_processor = FrameProcessor()
        
        logger.info(f"StreamManager initialized (max {self.max_streams} streams)")
    
    def add_stream(
        self,
        camera_id: int,
        source: str,
        source_type: str
    ) -> bool:
        """Add new stream"""
        if len(self.streams) >= self.max_streams:
            logger.warning(f"Maximum streams ({self.max_streams}) reached")
            return False
        
        if camera_id in self.streams:
            logger.warning(f"Stream {camera_id} already exists")
            return False
        
        try:
            # Create ingestor
            ingestor = VideoIngestor(source, source_type)
            if not ingestor.start():
                return False
            
            self.streams[camera_id] = ingestor
            self.frame_queues[camera_id] = queue.Queue(maxsize=30)
            
            # Start processing thread
            thread = threading.Thread(
                target=self._process_stream,
                args=(camera_id,),
                daemon=True
            )
            thread.start()
            self.processors[camera_id] = thread
            
            logger.info(f"Added stream {camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add stream {camera_id}: {e}")
            return False
    
    def remove_stream(self, camera_id: int):
        """Remove stream"""
        if camera_id not in self.streams:
            return
        
        # Stop ingestor
        self.streams[camera_id].stop()
        del self.streams[camera_id]
        
        # Clean up queue
        if camera_id in self.frame_queues:
            del self.frame_queues[camera_id]
        
        # Thread will stop automatically when ingestor stops
        if camera_id in self.processors:
            del self.processors[camera_id]
        
        logger.info(f"Removed stream {camera_id}")
    
    def _process_stream(self, camera_id: int):
        """Process single stream (runs in separate thread)"""
        logger.info(f"Processing thread started for camera {camera_id}")
        frame_count = 0
        
        while camera_id in self.streams:
            try:
                ingestor = self.streams[camera_id]
                success, frame = ingestor.read_frame()
                
                if not success or frame is None:
                    time.sleep(0.1)
                    continue
                
                # Process frame
                results = self.frame_processor.process_frame(
                    frame,
                    camera_id,
                    frame_count
                )
                
                # Put results in queue
                try:
                    self.frame_queues[camera_id].put_nowait({
                        'frame': frame,
                        'results': results,
                        'frame_id': frame_count
                    })
                except queue.Full:
                    # Drop frame if queue is full
                    pass
                
                frame_count += 1
                
                # Rate limiting
                time.sleep(1.0 / settings.FRAME_RATE)
                
            except Exception as e:
                logger.error(f"Error processing stream {camera_id}: {e}")
                time.sleep(1.0)
        
        logger.info(f"Processing thread stopped for camera {camera_id}")
    
    def get_latest_frame(self, camera_id: int) -> Optional[Dict]:
        """Get latest processed frame for a camera"""
        if camera_id not in self.frame_queues:
            return None
        
        try:
            return self.frame_queues[camera_id].get_nowait()
        except queue.Empty:
            return None
    
    def get_active_streams(self) -> List[int]:
        """Get list of active camera IDs"""
        return list(self.streams.keys())
    
    def stop_all(self):
        """Stop all streams"""
        logger.info("Stopping all streams")
        for camera_id in list(self.streams.keys()):
            self.remove_stream(camera_id)
