# ============================================================================
# backend/scripts/init_db.py - Database Initialization Script
# ============================================================================

"""
Initialize database with default data:
- Create admin and operator users
- Create default cameras (including webcam)
- Create sample watchlist entries
"""

from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base, init_db
from backend.models.user import User, UserRole
from backend.models.camera import Camera
from backend.models.watchlist import WatchlistEntry, WatchlistType
from backend.models.federated import FederatedNode
from backend.utils.security import get_password_hash
from backend.utils.logger import setup_logger
import datetime

logger = setup_logger(__name__)


def create_default_users(db: Session):
    """Create default admin and operator users"""
    
    # Check if admin already exists
    admin = db.query(User).filter(User.username == 'admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@sentinel.ai',
            hashed_password=get_password_hash('admin123'),
            full_name='System Administrator',
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        logger.info("Created admin user: admin / admin123")
    
    # Check if operator already exists
    operator = db.query(User).filter(User.username == 'operator').first()
    if not operator:
        operator = User(
            username='operator',
            email='operator@sentinel.ai',
            hashed_password=get_password_hash('operator123'),
            full_name='System Operator',
            role=UserRole.OPERATOR,
            is_active=True
        )
        db.add(operator)
        logger.info("Created operator user: operator / operator123")
    
    db.commit()


def create_default_cameras(db: Session):
    """Create default cameras including webcam"""
    
    # Check if cameras already exist
    existing = db.query(Camera).count()
    if existing > 0:
        logger.info(f"Cameras already exist ({existing}), skipping...")
        return
    
    cameras = [
        {
            'name': 'Entrance Camera',
            'location': 'Main Entrance',
            'zone': 'entrance',
            'source_type': 'webcam',
            'source_url': '0',  # Default webcam
            'enabled': True,
            'status': 'offline'
        },
        {
            'name': 'Parking Camera',
            'location': 'Parking Lot',
            'zone': 'parking',
            'source_type': 'webcam',
            'source_url': '0',  # Default webcam (same for demo)
            'enabled': True,
            'status': 'offline'
        }
    ]
    
    for cam_data in cameras:
        camera = Camera(**cam_data)
        db.add(camera)
        logger.info(f"Created camera: {cam_data['name']}")
    
    db.commit()


def create_sample_watchlist(db: Session):
    """Create sample watchlist entries for testing"""
    
    # Check if entries already exist
    existing = db.query(WatchlistEntry).count()
    if existing > 0:
        logger.info(f"Watchlist entries already exist ({existing}), skipping...")
        return
    
    # Sample criminals
    criminals = [
        {
            'entry_type': WatchlistType.CRIMINAL,
            'synthetic_id': 'CRIM_001',
            'name': 'John Doe (Synthetic)',
            'age': 35,
            'description': 'Synthetic test subject for fraud detection',
            'risk_level': 'high',
            'is_active': True
        },
        {
            'entry_type': WatchlistType.CRIMINAL,
            'synthetic_id': 'CRIM_002',
            'name': 'Jane Smith (Synthetic)',
            'age': 28,
            'description': 'Synthetic test subject for theft detection',
            'risk_level': 'medium',
            'is_active': True
        }
    ]
    
    # Sample missing persons
    missing = [
        {
            'entry_type': WatchlistType.MISSING,
            'synthetic_id': 'MISS_001',
            'name': 'Alex Johnson (Synthetic)',
            'age': 16,
            'age_at_disappearance': 14,
            'description': 'Synthetic missing person for testing age progression',
            'last_seen_location': 'Downtown Area',
            'last_seen_date': datetime.datetime.now() - datetime.timedelta(days=730),
            'is_active': True
        }
    ]
    
    for entry_data in criminals + missing:
        entry = WatchlistEntry(**entry_data)
        db.add(entry)
        logger.info(f"Created watchlist entry: {entry_data['synthetic_id']}")
    
    db.commit()


def create_federated_nodes(db: Session):
    """Create sample federated learning nodes"""
    
    # Check if nodes already exist
    existing = db.query(FederatedNode).count()
    if existing > 0:
        logger.info(f"Federated nodes already exist ({existing}), skipping...")
        return
    
    nodes = [
        {
            'node_id': 'node_001',
            'name': 'Primary Node',
            'location': 'Main Server',
            'status': 'active',
            'total_samples': 1000,
            'model_version': 1
        },
        {
            'node_id': 'node_002',
            'name': 'Secondary Node',
            'location': 'Edge Server 1',
            'status': 'active',
            'total_samples': 800,
            'model_version': 1
        },
        {
            'node_id': 'node_003',
            'name': 'Tertiary Node',
            'location': 'Edge Server 2',
            'status': 'active',
            'total_samples': 600,
            'model_version': 1
        }
    ]
    
    for node_data in nodes:
        node = FederatedNode(**node_data)
        db.add(node)
        logger.info(f"Created federated node: {node_data['node_id']}")
    
    db.commit()


def initialize_database():
    """Main initialization function"""
    
    logger.info("=" * 80)
    logger.info("SENTINEL AI - Database Initialization")
    logger.info("=" * 80)
    
    # Create all tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Create default data
        logger.info("\nInitializing default data...")
        
        create_default_users(db)
        logger.info("✓ Default users created")
        
        create_default_cameras(db)
        logger.info("✓ Default cameras created")
        
        create_sample_watchlist(db)
        logger.info("✓ Sample watchlist entries created")
        
        create_federated_nodes(db)
        logger.info("✓ Federated nodes created")
        
        logger.info("\n" + "=" * 80)
        logger.info("DATABASE INITIALIZATION COMPLETE!")
        logger.info("=" * 80)
        logger.info("\nDefault Credentials:")
        logger.info("  Admin: admin / admin123")
        logger.info("  Operator: operator / operator123")
        logger.info("\nYou can now start the application:")
        logger.info("  uvicorn backend.main:app --reload")
        logger.info("=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()