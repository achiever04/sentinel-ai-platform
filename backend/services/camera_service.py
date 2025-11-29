# ============================================================================
# backend/services/camera_service.py - FIXED VERSION
# ============================================================================

from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from fastapi import HTTPException, status
from backend.models.camera import Camera
from backend.processors.video_ingestor import VideoIngestor
from backend.utils.logger import setup_logger 
import datetime

logger = setup_logger(__name__)

class CameraService:
    """Service for managing cameras and video sources"""
    
    # Class-level dictionary to store active streams
    active_streams: Dict[int, VideoIngestor] = {}
    
    @staticmethod
    def create_camera(db: Session, camera_data: Dict) -> Camera:
        """Create new camera"""
        camera = Camera(
            name=camera_data['name'],
            location=camera_data.get('location'),
            zone=camera_data.get('zone'),
            source_type=camera_data['source_type'],
            source_url=camera_data['source_url'],
            enabled=camera_data.get('enabled', True)
        )
        db.add(camera)
        db.commit()
        db.refresh(camera)
        logger.info(f"Camera created: {camera.name} (ID: {camera.id})")
        return camera
    
    @staticmethod
    def get_camera(db: Session, camera_id: int) -> Optional[Camera]:
        """Get camera by ID"""
        return db.query(Camera).filter(Camera.id == camera_id).first()
    
    @staticmethod
    def list_cameras(db: Session, enabled_only: bool = False) -> List[Camera]:
        """List all cameras"""
        query = db.query(Camera)
        if enabled_only:
            query = query.filter(Camera.enabled == True)
        return query.all()
    
    @staticmethod
    def update_camera(db: Session, camera_id: int, update_data: Dict) -> Camera:
        """Update camera details"""
        camera = CameraService.get_camera(db, camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Camera not found"
            )
        
        for key, value in update_data.items():
            if hasattr(camera, key):
                setattr(camera, key, value)
        
        db.commit()
        db.refresh(camera)
        return camera
    
    @staticmethod
    def delete_camera(db: Session, camera_id: int) -> bool:
        """Delete camera"""
        camera = CameraService.get_camera(db, camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Camera not found"
            )
        
        # Stop stream if active
        if camera_id in CameraService.active_streams:
            CameraService.stop_stream(camera_id)
        
        db.delete(camera)
        db.commit()
        return True
    
    @staticmethod
    def start_stream(camera_id: int, camera: Camera) -> bool:
        """
        Start video stream for camera
        
        IMPORTANT: This creates ONE VideoIngestor that will be used by WebSocket
        """
        if camera_id in CameraService.active_streams:
            logger.warning(f"Stream already active for camera {camera_id}")
            return True
        
        try:
            # Create VideoIngestor
            ingestor = VideoIngestor(
                source=camera.source_url,
                source_type=camera.source_type
            )
            
            # Start the ingestor
            if ingestor.start():
                # Store in class-level dictionary
                CameraService.active_streams[camera_id] = ingestor
                logger.info(f"Stream started for camera {camera_id}")
                return True
            else:
                logger.error(f"Failed to start ingestor for camera {camera_id}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to start stream for camera {camera_id}: {e}")
            return False
    
    @staticmethod
    def stop_stream(camera_id: int):
        """Stop video stream for camera"""
        if camera_id in CameraService.active_streams:
            try:
                CameraService.active_streams[camera_id].stop()
                del CameraService.active_streams[camera_id]
                logger.info(f"Stream stopped for camera {camera_id}")
            except Exception as e:
                logger.error(f"Error stopping stream for camera {camera_id}: {e}")
    
    @staticmethod
    def get_stream_status(camera_id: int) -> Dict:
        """Get stream status"""
        is_active = camera_id in CameraService.active_streams
        return {
            'camera_id': camera_id,
            'is_active': is_active,
            'status': 'online' if is_active else 'offline'
        }