# ============================================================================
# update_cameras.py - FIXED VERSION with Camera Index Detection
# ============================================================================

from backend.database import SessionLocal
from backend.models.camera import Camera
from backend.utils.logger import setup_logger
import cv2

logger = setup_logger(__name__)

def find_working_camera():
    """Find the first working camera index"""
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None:
                logger.info(f"✅ Found working camera at index {i}")
                return i
    
    logger.error("❌ No working camera found!")
    return None

def update_cameras():
    """Update all cameras to use the working webcam"""
    db = SessionLocal()
    
    try:
        # Find working camera
        camera_index = find_working_camera()
        
        if camera_index is None:
            logger.error("Cannot update cameras - no working camera found")
            logger.error("Please check:")
            logger.error("  1. Is webcam connected?")
            logger.error("  2. Close other apps using camera (Chrome, Zoom)")
            logger.error("  3. Run: ./fix_camera_permissions.sh")
            return False
        
        # Update all cameras
        cameras = db.query(Camera).all()
        
        if not cameras:
            logger.warning("No cameras in database. Creating default camera...")
            camera = Camera(
                name="Default Webcam",
                location="Local System",
                zone="entrance",
                source_type="webcam",
                source_url=str(camera_index),
                enabled=True
            )
            db.add(camera)
            db.commit()
            logger.info(f"✅ Created default camera using index {camera_index}")
            return True
        
        # Update existing cameras
        for camera in cameras:
            logger.info(f"Updating camera {camera.id}: {camera.name}")
            camera.source_type = 'webcam'
            camera.source_url = str(camera_index)
        
        db.commit()
        logger.info(f"✅ Updated {len(cameras)} cameras to use webcam index {camera_index}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Camera Update Script")
    logger.info("=" * 60)
    success = update_cameras()
    if success:
        logger.info("\n✅ Success! You can now start the cameras.")
    else:
        logger.error("\n❌ Failed. Please fix the issues above.")