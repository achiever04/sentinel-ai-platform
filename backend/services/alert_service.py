# ============================================================================
# backend/services/alert_service.py - Alert Management Service
# ============================================================================

from fastapi import HTTPException
from grpc import Status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from backend.models.alert import Alert
from backend.utils.notifications import send_email_alert
from backend.utils.voice_alert import speak_alert
from backend.config import get_settings
from backend.utils.logger import setup_logger
from datetime import datetime

settings = get_settings()
logger = setup_logger(__name__)

class AlertService:
    """Service for managing alerts and notifications"""
    
    @staticmethod
    def create_alert(db: Session, alert_data: Dict) -> Alert:
        """Create new alert"""
        alert = Alert(
            alert_type=alert_data['alert_type'],
            severity=alert_data['severity'],
            camera_id=alert_data.get('camera_id'),
            person_id=alert_data.get('person_id'),
            detection_id=alert_data.get('detection_id'),
            watchlist_match_id=alert_data.get('watchlist_match_id'),
            title=alert_data['title'],
            message=alert_data['message'],
            metadata=alert_data.get('metadata', {})
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        # Send notifications
        AlertService._send_notifications(alert)
        
        logger.info(f"Alert created: {alert.alert_type} - {alert.title}")
        return alert
    
    @staticmethod
    def _send_notifications(alert: Alert):
        """Send alert notifications"""
        # Voice alert
        if settings.ENABLE_VOICE_ALERTS and alert.severity in ['warning', 'critical']:
            try:
                speak_alert(alert.message)
                alert.voice_alert_sent = True
            except Exception as e:
                logger.error(f"Failed to send voice alert: {e}")
        
        # Email alert
        if settings.ENABLE_EMAIL_ALERTS:
            try:
                send_email_alert(alert.title, alert.message)
                alert.email_alert_sent = True
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
    
    @staticmethod
    def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
        """Get alert by ID"""
        return db.query(Alert).filter(Alert.id == alert_id).first()
    
    @staticmethod
    def list_alerts(
        db: Session,
        camera_id: Optional[int] = None,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        limit: int = 100
    ) -> List[Alert]:
        """List alerts with filters"""
        query = db.query(Alert)
        
        if camera_id:
            query = query.filter(Alert.camera_id == camera_id)
        if severity:
            query = query.filter(Alert.severity == severity)
        if acknowledged is not None:
            query = query.filter(Alert.acknowledged == acknowledged)
        
        return query.order_by(Alert.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def acknowledge_alert(db: Session, alert_id: int, user_id: int) -> Alert:
        """Acknowledge alert"""
        alert = AlertService.get_alert(db, alert_id)
        if not alert:
            raise HTTPException(
                status_code=Status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        alert.acknowledged = True
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.now()
        
        db.commit()
        db.refresh(alert)
        return alert