# ============================================================================
# backend/utils/__init__.py
# ============================================================================

"""
Utility Functions Package

Helper functions, validators, and utility tools
"""

from backend.utils.logger import setup_logger, logger
from backend.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from backend.utils.validators import (
    validate_email,
    validate_username,
    validate_password_strength,
    validate_coordinates,
    validate_confidence,
    validate_file_extension,
    sanitize_filename
)
from backend.utils.notifications import send_email_alert
from backend.utils.voice_alert import speak_alert, get_tts_engine

__all__ = [
    # Logging
    "setup_logger",
    "logger",
    
    # Security
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    
    # Validators
    "validate_email",
    "validate_username",
    "validate_password_strength",
    "validate_coordinates",
    "validate_confidence",
    "validate_file_extension",
    "sanitize_filename",
    
    # Notifications
    "send_email_alert",
    "speak_alert",
    "get_tts_engine",
]