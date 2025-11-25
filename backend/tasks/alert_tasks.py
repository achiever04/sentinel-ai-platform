# ============================================================================
# backend/tasks/alert_tasks.py - Alert Processing Tasks
# ============================================================================

from backend.tasks.celery_app import celery_app
from backend.utils.logger import setup_logger
from backend.utils.voice_alert import speak_alert
from backend.utils.notifications import send_email_alert

logger = setup_logger(__name__)

@celery_app.task(name='send_alert_notifications')
def send_alert_notifications(alert_id: int, alert_data: dict):
    """Send alert notifications (voice, email)"""
    logger.info(f"Sending notifications for alert {alert_id}")
    
    try:
        # Voice alert
        if alert_data.get('send_voice'):
            speak_alert(alert_data['message'], async_speak=False)
        
        # Email alert
        if alert_data.get('send_email'):
            send_email_alert(
                alert_data['title'],
                alert_data['message'],
                alert_data.get('recipient')
            )
        
        return {'status': 'sent'}
        
    except Exception as e:
        logger.error(f"Error sending alerts: {e}")
        return {'status': 'failed', 'error': str(e)}
