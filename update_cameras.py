# ============================================================================
# update_cameras.py - Change camera sources from synthetic to webcam
# ============================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models.camera import Camera
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def update_cameras():
    """Update all cameras to use webcam instead of synthetic"""
    db = SessionLocal()
    
    try:
        cameras = db.query(Camera).all()
        
        for camera in cameras:
            if camera.source_type == 'synthetic':
                logger.info(f"Updating camera {camera.id}: {camera.name}")
                camera.source_type = 'webcam'
                camera.source_url = '0'  # Default webcam
        
        db.commit()
        logger.info(f"✅ Updated {len(cameras)} cameras to use webcam")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    update_cameras()
