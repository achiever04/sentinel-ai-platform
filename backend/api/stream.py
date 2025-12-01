# ============================================================================
# backend/api/stream.py - WebSocket Camera Streaming - FIXED VERSION
# ============================================================================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import base64
import asyncio
from datetime import datetime
from backend.database import SessionLocal
from backend.models.camera import Camera
from backend.services.camera_service import CameraService
from backend.processors.frame_processor import FrameProcessor
from backend.utils.logger import setup_logger

router = APIRouter(prefix="/api/stream", tags=["Streaming"])
logger = setup_logger(__name__)

frame_processor = FrameProcessor()


@router.websocket("/ws/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: int):
    """
    WebSocket endpoint for real-time camera streaming
    
    FIXED: Removed Depends(get_db) - WebSockets don't support it
    Uses manual SessionLocal() instead
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for camera {camera_id}")
    
    # Manual database session (WebSockets can't use Depends)
    db = SessionLocal()
    
    try:
        # Get camera from database
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        
        if not camera:
            logger.error(f"Camera {camera_id} not found in database")
            await websocket.close(code=1008, reason="Camera not found")
            return
        
        # Check if camera stream is active in CameraService
        if camera_id not in CameraService.active_streams:
            logger.error(f"Camera {camera_id} stream not active")
            await websocket.close(code=1011, reason="Camera stream not started")
            return
        
        # Get the active VideoIngestor from CameraService
        ingestor = CameraService.active_streams[camera_id]
        frame_count = 0
        
        logger.info(f"Starting frame transmission for camera {camera_id}")
        
        while True:
            try:
                # Non-blocking check for client disconnect
                try:
                    message = await asyncio.wait_for(websocket.receive_text(), timeout=0.001)
                    if message == "ping":
                        await websocket.send_text("pong")
                except asyncio.TimeoutError:
                    pass
                except:
                    logger.info(f"Client disconnected from camera {camera_id}")
                    break
                
                # Read frame from the EXISTING ingestor (no duplicate opening)
                ret, frame = ingestor.read_frame()
                
                if not ret or frame is None:
                    await asyncio.sleep(0.1)
                    continue
                
                # Resize frame for transmission
                frame = cv2.resize(frame, (640, 480))
                
                # Process every 3rd frame to reduce CPU load
                detections = []
                if frame_count % 3 == 0:
                    try:
                        results = frame_processor.process_frame(
                            frame,
                            camera_id,
                            frame_count
                        )
                        detections = results.get('detections', [])
                        
                        # Draw detections on frame
                        frame = frame_processor.draw_detections(frame, detections)
                    except Exception as e:
                        logger.error(f"Error processing frame: {e}")
                        # Continue anyway - send raw frame
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Send frame via WebSocket
                try:
                    await websocket.send_json({
                        'type': 'frame',
                        'camera_id': camera_id,
                        'frame': frame_base64,
                        'frame_count': frame_count,
                        'detections': len(detections),
                        'detection_data': detections[:5]  # Only first 5
                    })
                except Exception as e:
                    logger.error(f"Failed to send frame: {e}")
                    break
                
                frame_count += 1
                
                # Control frame rate (~15 FPS)
                await asyncio.sleep(0.066)
            
            except Exception as e:
                logger.error(f"Error in frame loop: {e}")
                break
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for camera {camera_id}")
    except Exception as e:
        logger.error(f"WebSocket error for camera {camera_id}: {e}")
    finally:
        db.close()
        logger.info(f"WebSocket closed for camera {camera_id}")


@router.get("/{camera_id}/snapshot")
async def get_snapshot(camera_id: int):
    """
    Get a single snapshot from camera
    
    Returns base64-encoded JPEG image
    """
    db = SessionLocal()
    
    try:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        
        if not camera:
            return {"error": "Camera not found"}
        
        # Check if stream is active
        if camera_id not in CameraService.active_streams:
            return {"error": "Camera stream not active"}
        
        ingestor = CameraService.active_streams[camera_id]
        ret, frame = ingestor.read_frame()
        
        if not ret or frame is None:
            return {"error": "Failed to capture frame"}
        
        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "camera_id": camera_id,
            "snapshot": frame_base64,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error capturing snapshot: {e}")
        return {"error": str(e)}
    finally:
        db.close()