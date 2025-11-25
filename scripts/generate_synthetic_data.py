# ============================================================================
# scripts/generate_synthetic_data.py - Generate Test Data
# ============================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from pathlib import Path
from backend.config import get_settings
from backend.utils.logger import setup_logger
from backend.database import SessionLocal
from backend.models.camera import Camera
from backend.models.watchlist import WatchlistEntry, WatchlistType

settings = get_settings()
logger = setup_logger(__name__)

def generate_synthetic_faces(num_faces: int = 20):
    """Generate synthetic face images for testing"""
    faces_dir = Path(settings.FACES_DIR)
    faces_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Generating {num_faces} synthetic faces...")
    
    for i in range(num_faces):
        # Create synthetic face image (colored rectangle with circle for face)
        img = np.random.randint(150, 200, (200, 150, 3), dtype=np.uint8)
        
        # Add face-like features
        # Face oval
        cv2.ellipse(img, (75, 100), (50, 70), 0, 0, 360, (255, 220, 180), -1)
        
        # Eyes
        cv2.circle(img, (60, 85), 8, (0, 0, 0), -1)
        cv2.circle(img, (90, 85), 8, (0, 0, 0), -1)
        
        # Mouth
        cv2.ellipse(img, (75, 120), (20, 10), 0, 0, 180, (100, 50, 50), 2)
        
        # Save
        filename = f"synthetic_face_{i:03d}.jpg"
        cv2.imwrite(str(faces_dir / filename), img)
    
    logger.info(f"Synthetic faces saved to {faces_dir}")

def create_sample_cameras():
    """Create sample camera configurations"""
    db = SessionLocal()
    
    logger.info("Creating sample cameras...")
    
    cameras_data = [
        {
            "name": "Entrance Camera",
            "location": "Main Entrance",
            "zone": "entrance",
            "source_type": "synthetic",
            "source_url": "synthetic://camera1",
            "enabled": True
        },
        {
            "name": "Parking Camera",
            "location": "Parking Lot",
            "zone": "parking",
            "source_type": "synthetic",
            "source_url": "synthetic://camera2",
            "enabled": True
        },
        {
            "name": "Corridor Camera",
            "location": "Main Corridor",
            "zone": "corridor",
            "source_type": "synthetic",
            "source_url": "synthetic://camera3",
            "enabled": True
        },
        {
            "name": "Exit Camera",
            "location": "Exit Gate",
            "zone": "exit",
            "source_type": "synthetic",
            "source_url": "synthetic://camera4",
            "enabled": True
        }
    ]
    
    try:
        for cam_data in cameras_data:
            existing = db.query(Camera).filter(Camera.name == cam_data['name']).first()
            if not existing:
                camera = Camera(**cam_data)
                db.add(camera)
        
        db.commit()
        logger.info(f"Created {len(cameras_data)} sample cameras")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create cameras: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def create_synthetic_watchlist():
    """Create synthetic watchlist entries"""
    db = SessionLocal()
    
    logger.info("Creating synthetic watchlist entries...")
    
    # Synthetic criminals
    criminals = [
        {
            "entry_type": WatchlistType.CRIMINAL,
            "synthetic_id": "CRIM_001",
            "name": "John Synthetic",
            "age": 35,
            "description": "Simulated high-risk individual for testing",
            "risk_level": "high",
            "face_images": ["synthetic_face_001.jpg"],
            "is_active": True
        },
        {
            "entry_type": WatchlistType.CRIMINAL,
            "synthetic_id": "CRIM_002",
            "name": "Jane Simulation",
            "age": 28,
            "description": "Simulated medium-risk individual for testing",
            "risk_level": "medium",
            "face_images": ["synthetic_face_002.jpg"],
            "is_active": True
        }
    ]
    
    # Synthetic missing persons
    missing = [
        {
            "entry_type": WatchlistType.MISSING,
            "synthetic_id": "MISS_001",
            "name": "Tommy Virtual",
            "age": 12,
            "age_at_disappearance": 10,
            "description": "Simulated missing child for testing age progression",
            "last_seen_location": "Simulated Park",
            "face_images": ["synthetic_face_010.jpg"],
            "is_active": True
        },
        {
            "entry_type": WatchlistType.MISSING,
            "synthetic_id": "MISS_002",
            "name": "Sarah Digital",
            "age": 45,
            "age_at_disappearance": 43,
            "description": "Simulated missing person for testing",
            "last_seen_location": "Simulated Mall",
            "face_images": ["synthetic_face_011.jpg"],
            "is_active": True
        }
    ]
    
    try:
        for entry_data in criminals + missing:
            existing = db.query(WatchlistEntry).filter(
                WatchlistEntry.synthetic_id == entry_data['synthetic_id']
            ).first()
            
            if not existing:
                entry = WatchlistEntry(**entry_data)
                db.add(entry)
        
        db.commit()
        logger.info(f"Created {len(criminals + missing)} watchlist entries")
        logger.info("NOTE: All watchlist entries are SYNTHETIC for academic use only!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create watchlist: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def generate_sample_videos():
    """Generate sample test videos"""
    videos_dir = Path(settings.VIDEOS_DIR)
    videos_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Generating sample test videos...")
    
    # Create simple test video (30 seconds, 15 fps)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width, height = 640, 480
    fps = 15
    
    for cam_num in range(1, 5):
        filename = videos_dir / f"sample_camera_{cam_num}.mp4"
        writer = cv2.VideoWriter(str(filename), fourcc, fps, (width, height))
        
        for frame_num in range(fps * 30):  # 30 seconds
            # Create frame with moving rectangle (simulated person)
            frame = np.random.randint(20, 50, (height, width, 3), dtype=np.uint8)
            
            # Moving "person"
            x = int((frame_num / (fps * 30)) * (width - 100))
            y = height // 2 - 75
            
            cv2.rectangle(frame, (x, y), (x + 80, y + 150), (100, 150, 200), -1)
            cv2.circle(frame, (x + 40, y + 30), 20, (255, 220, 180), -1)
            
            writer.write(frame)
        
        writer.release()
        logger.info(f"Created {filename}")
    
    logger.info(f"Sample videos saved to {videos_dir}")

def main():
    """Generate all synthetic test data"""
    logger.info("=== Generating Synthetic Test Data ===")
    logger.info("REMINDER: All data is SYNTHETIC for academic purposes only!")
    
    # Generate synthetic faces
    generate_synthetic_faces(20)
    
    # Create sample cameras
    create_sample_cameras()
    
    # Create synthetic watchlist
    create_synthetic_watchlist()
    
    # Generate sample videos
    generate_sample_videos()
    
    logger.info("=== Data Generation Complete ===")

if __name__ == "__main__":
    main()
