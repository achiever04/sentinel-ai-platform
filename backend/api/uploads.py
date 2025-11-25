# ============================================================================
# backend/api/uploads.py - File Upload API Routes
# ============================================================================

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.auth_service import get_current_active_user
from backend.models.user import User
from backend.config import get_settings
from backend.utils.validators import validate_file_extension, sanitize_filename
import cv2
import numpy as np
from pathlib import Path
import uuid
import os  # ADDED - This was missing

router = APIRouter(prefix="/api/uploads", tags=["Uploads"])
settings = get_settings()

ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp']
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov', 'mkv']

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    purpose: str = "general",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload image file
    
    Purpose: 'watchlist', 'search', 'general'
    ACADEMIC: Only synthetic faces allowed
    """
    # Validate file extension
    if not validate_file_extension(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{safe_filename}"
    
    # Save file
    upload_path = Path(settings.UPLOADS_DIR) / unique_filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    
    contents = await file.read()
    with open(upload_path, 'wb') as f:
        f.write(contents)
    
    # Validate it's an image
    try:
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            upload_path.unlink()
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        height, width = image.shape[:2]
    except Exception as e:
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    
    return {
        "filename": unique_filename,
        "path": str(upload_path),
        "size": len(contents),
        "dimensions": {"width": width, "height": height},
        "purpose": purpose
    }

@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload video file for processing"""
    # Validate file extension
    if not validate_file_extension(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Invalid video file type")
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{safe_filename}"
    
    # Save file
    upload_path = Path(settings.VIDEOS_DIR) / unique_filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    
    contents = await file.read()
    with open(upload_path, 'wb') as f:
        f.write(contents)
    
    # Get video info
    try:
        cap = cv2.VideoCapture(str(upload_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        duration = frame_count / fps if fps > 0 else 0
        
    except Exception as e:
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=400, detail=f"Error processing video: {str(e)}")
    
    return {
        "filename": unique_filename,
        "path": str(upload_path),
        "size": len(contents),
        "video_info": {
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "duration_seconds": duration
        }
    }

@router.post("/batch-images")
async def upload_batch_images(
    files: list[UploadFile] = File(...),
    purpose: str = "general",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload multiple images at once
    
    Useful for batch watchlist entry creation
    """
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 files allowed per batch")
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Validate file extension
            if not validate_file_extension(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                errors.append(f"{file.filename}: Invalid file type")
                continue
            
            # Sanitize filename
            safe_filename = sanitize_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{safe_filename}"
            
            # Save file
            upload_path = Path(settings.UPLOADS_DIR) / unique_filename
            upload_path.parent.mkdir(parents=True, exist_ok=True)
            
            contents = await file.read()
            with open(upload_path, 'wb') as f:
                f.write(contents)
            
            # Validate it's an image
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                upload_path.unlink()
                errors.append(f"{file.filename}: Invalid image file")
                continue
            
            height, width = image.shape[:2]
            
            uploaded_files.append({
                "original_filename": file.filename,
                "saved_filename": unique_filename,
                "path": str(upload_path),
                "size": len(contents),
                "dimensions": {"width": width, "height": height}
            })
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    return {
        "uploaded": len(uploaded_files),
        "failed": len(errors),
        "files": uploaded_files,
        "errors": errors if errors else None,
        "purpose": purpose
    }

@router.delete("/file/{filename}")
async def delete_uploaded_file(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an uploaded file"""
    # Sanitize filename to prevent path traversal
    safe_filename = sanitize_filename(filename)
    
    # Try to find file in uploads or videos directory
    upload_path = Path(settings.UPLOADS_DIR) / safe_filename
    video_path = Path(settings.VIDEOS_DIR) / safe_filename
    
    deleted = False
    
    if upload_path.exists():
        upload_path.unlink()
        deleted = True
    elif video_path.exists():
        video_path.unlink()
        deleted = True
    
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "message": "File deleted successfully",
        "filename": safe_filename
    }

@router.get("/list")
async def list_uploaded_files(
    file_type: str = "all",  # 'images', 'videos', or 'all'
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all uploaded files"""
    files = []
    
    # List images
    if file_type in ['images', 'all']:
        upload_dir = Path(settings.UPLOADS_DIR)
        if upload_dir.exists():
            for file_path in upload_dir.glob('*'):
                if file_path.is_file():
                    files.append({
                        "filename": file_path.name,
                        "type": "image",
                        "size": file_path.stat().st_size,
                        "created": file_path.stat().st_ctime
                    })
    
    # List videos
    if file_type in ['videos', 'all']:
        video_dir = Path(settings.VIDEOS_DIR)
        if video_dir.exists():
            for file_path in video_dir.glob('*'):
                if file_path.is_file():
                    files.append({
                        "filename": file_path.name,
                        "type": "video",
                        "size": file_path.stat().st_size,
                        "created": file_path.stat().st_ctime
                    })
    
    # Sort by creation time (newest first)
    files.sort(key=lambda x: x['created'], reverse=True)
    
    return {
        "total": len(files),
        "files": files
    }