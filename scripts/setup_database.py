#!/usr/bin/env python3

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base, init_db
from backend.utils.logger import setup_logger

# Import all models to register them
from backend.models.user import User
from backend.models.camera import Camera
from backend.models.person import Person
from backend.models.detection import Detection
from backend.models.track import Track
from backend.models.watchlist import WatchlistEntry, WatchlistMatch
from backend.models.alert import Alert
from backend.models.federated import FederatedNode, FederatedRound, FederatedUpdate

logger = setup_logger(__name__)

def setup_database():
    """Initialize database tables"""
    try:
        logger.info("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database tables created successfully!")
        logger.info(f"Tables created: {', '.join(Base.metadata.tables.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
