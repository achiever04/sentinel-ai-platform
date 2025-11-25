# ============================================================================
# scripts/create_admin.py - Create Default Admin User
# ============================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.services.auth_service import AuthService, UserCreate
from backend.models.user import UserRole
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def create_admin_user():
    """Create default admin and operator users"""
    db = SessionLocal()
    
    try:
        # Create admin user
        admin_data = UserCreate(
            username="admin",
            email="admin@sentinel.ai",
            password="admin123",
            full_name="System Administrator",
            role=UserRole.ADMIN
        )
        
        try:
            admin = AuthService.create_user(db, admin_data)
            logger.info(f"Admin user created: {admin.username}")
        except Exception as e:
            logger.warning(f"Admin user may already exist: {e}")
        
        # Create operator user
        operator_data = UserCreate(
            username="operator",
            email="operator@sentinel.ai",
            password="operator123",
            full_name="System Operator",
            role=UserRole.OPERATOR
        )
        
        try:
            operator = AuthService.create_user(db, operator_data)
            logger.info(f"Operator user created: {operator.username}")
        except Exception as e:
            logger.warning(f"Operator user may already exist: {e}")
        
        logger.info("\n=== Default Credentials ===")
        logger.info("Admin - username: admin, password: admin123")
        logger.info("Operator - username: operator, password: operator123")
        logger.info("===========================\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create users: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_admin_user()
    sys.exit(0 if success else 1)
