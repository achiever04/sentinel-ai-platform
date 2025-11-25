# ============================================================================
# backend/utils/notifications.py - Notification Utilities
# ============================================================================

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)

def send_email_alert(subject: str, message: str, recipient: str = None):
    """
    Send email alert
    
    Note: Configure SMTP settings in .env for production use
    This is a placeholder implementation for demonstration
    """
    try:
        # Email configuration (placeholder - configure in .env)
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "alerts@sentinel.ai")
        sender_password = os.getenv("SENDER_PASSWORD", "")
        
        if not sender_password:
            logger.warning("Email alerts not configured - skipping email send")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient or sender_email
        msg['Subject'] = f"[Sentinel AI] {subject}"
        
        body = f"""
        Sentinel AI Alert
        
        {message}
        
        ---
        This is an automated alert from Sentinel AI Platform.
        ACADEMIC SYSTEM - For demonstration purposes only.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        logger.info(f"Email alert sent: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")
        return False
