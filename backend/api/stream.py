# ============================================================================
# backend/api/stream.py - WebSocket Camera Streaming
# ============================================================================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import cv2
import numpy as np
import base64
import asyncio
import json
from typing import Dict
from backend.database import get_db
from backend.services.camera_service import CameraService
from backend.processors.frame_processor import FrameProcessor
from backend.utils.logger import setup_logger
from datetime import datetime

router = APIRouter(prefix="/api/stream", tags=["Streaming"])
logger = setup_logger(__name__)

# Active WebSocket connections: camera_id -> list of WebSocket connections
active_connections: Dict[int, list] = {}
frame_processor = FrameProcessor()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, list] = {}

    async def connect(self, websocket: WebSocket, camera_id: int):
        await websocket.accept()
        if camera_id not in self.active_connections:
            self.active_connections[camera_id] = []
        self.active_connections[camera_id].append(websocket)
        logger.info(f"WebSocket connected for camera {camera_id}")

    def disconnect(self, websocket: WebSocket, camera_id: int):
        if camera_id in self.active_connections:
            self.active_connections[camera_id].remove(websocket)
            if not self.active_connections[camera_id]:
                del self.active_connections[camera_id]
        logger.info(f"WebSocket disconnected for camera {camera_id}")

    async def broadcast(self, camera_id: int, message: dict):
        if camera_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[camera_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.append(connection)
            
            # Remove dead connections
            for conn in dead_connections:
                self.disconnect(conn, camera_id)


manager = ConnectionManager()


@router.websocket("/ws/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: int, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time camera streaming
    
    Sends frames as base64-encoded JPEG images with detection data
    """
    await manager.connect(websocket, camera_id)
    
    # Get camera from database
    camera = CameraService.get_camera(db, camera_id)
    if not camera:
        await websocket.close(code=1008, reason="Camera not found")
        return
    
    try:
        # Initialize video capture
        if camera.source_type == 'webcam':
            cap = cv2.VideoCapture(int(camera.source_url))
        elif camera.source_type == 'rtsp':
            cap = cv2.VideoCapture(camera.source_url)
        elif camera.source_type == 'file':
            cap = cv2.VideoCapture(camera.source_url)
        else:
            cap = cv2.VideoCapture(0)  # Default webcam
        
        if not cap.isOpened():
            await websocket.close(code=1011, reason="Failed to open camera")
            return
        
        frame_count = 0
        
        while True:
            # Check if client is still connected
            try:
                # Try to receive ping (non-blocking)
                message = await asyncio.wait_for(websocket.receive_text(), timeout=0.001)
                if message == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                pass
            
            # Read frame
            ret, frame = cap.read()
            if not ret:
                # Loop video if it's a file
                if camera.source_type == 'file':
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break
            
            # Resize frame for faster transmission
            frame = cv2.resize(frame, (640, 480))
            
            # Process frame every 3rd frame to save CPU
            detections = []
            if frame_count % 3 == 0:
                results = frame_processor.process_frame(
                    frame,
                    camera_id,
                    frame_count
                )
                detections = results.get('detections', [])
                
                # Draw detections on frame
                frame = frame_processor.draw_detections(frame, detections)
            
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send frame and detection data
            await websocket.send_json({
                'type': 'frame',
                'camera_id': camera_id,
                'frame': frame_base64,
                'frame_count': frame_count,
                'detections': len(detections),
                'detection_data': detections[:5]  # Send only first 5 detections to save bandwidth
            })
            
            frame_count += 1
            
            # Control frame rate (~15 FPS)
            await asyncio.sleep(0.066)
    
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from camera {camera_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket stream: {e}")
    finally:
        if 'cap' in locals():
            cap.release()
        manager.disconnect(websocket, camera_id)


@router.get("/{camera_id}/snapshot")
async def get_snapshot(camera_id: int, db: Session = Depends(get_db)):
    """
    Get a single snapshot from camera
    
    Returns base64-encoded JPEG image
    """
    camera = CameraService.get_camera(db, camera_id)
    if not camera:
        return {"error": "Camera not found"}
    
    try:
        # Open camera
        if camera.source_type == 'webcam':
            cap = cv2.VideoCapture(int(camera.source_url))
        else:
            cap = cv2.VideoCapture(camera.source_url)
        
        if not cap.isOpened():
            return {"error": "Failed to open camera"}
        
        # Read frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return {"error": "Failed to capture frame"}
        
        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "camera_id": camera_id,
            "snapshot": frame_base64,
            "timestamp": str(datetime.now())
        }
    
    except Exception as e:
        logger.error(f"Error capturing snapshot: {e}")
        return {"error": str(e)}