# ============================================================================
# backend/api/cameras.py - Camera API Routes
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.services.camera_service import CameraService
from backend.services.auth_service import get_current_active_user
from backend.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/cameras", tags=["Cameras"])

class CameraCreate(BaseModel):
    name: str
    location: str = None
    zone: str = None
    source_type: str
    source_url: str
    enabled: bool = True

class CameraResponse(BaseModel):
    id: int
    name: str
    location: str = None
    zone: str = None
    source_type: str
    status: str
    enabled: bool
    
    class Config:
        from_attributes = True

@router.post("/", response_model=CameraResponse)
async def create_camera(
    camera_data: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new camera (requires authentication)"""
    camera = CameraService.create_camera(db, camera_data.dict())
    return camera

@router.get("/", response_model=List[CameraResponse])
async def list_cameras(
    enabled_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all cameras"""
    cameras = CameraService.list_cameras(db, enabled_only)
    return cameras

@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get camera by ID"""
    camera = CameraService.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.post("/{camera_id}/start")
async def start_camera_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start camera stream"""
    camera = CameraService.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    success = CameraService.start_stream(camera_id, camera)
    return {"success": success, "message": "Stream started" if success else "Failed to start stream"}

@router.post("/{camera_id}/stop")
async def stop_camera_stream(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Stop camera stream"""
    CameraService.stop_stream(camera_id)
    
    # Update camera status in database
    camera = CameraService.get_camera(db, camera_id)
    if camera:
        camera.status = 'offline'
        db.commit()
    
    return {"success": True, "message": "Stream stopped"}
