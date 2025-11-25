# ============================================================================
# backend/utils/validators.py - Input Validators
# ============================================================================

import re
from typing import Optional
from fastapi import HTTPException, status

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username: str) -> bool:
    """Validate username (alphanumeric, underscore, hyphen)"""
    pattern = r'^[a-zA-Z0-9_-]{3,50}$'
    return re.match(pattern, username) is not None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"

def validate_coordinates(x: float, y: float, w: float, h: float) -> bool:
    """Validate bounding box coordinates"""
    return (0 <= x <= 1 and 0 <= y <= 1 and 
            0 < w <= 1 and 0 < h <= 1)

def validate_confidence(confidence: float) -> bool:
    """Validate confidence score (0-1)"""
    return 0.0 <= confidence <= 1.0

def validate_file_extension(filename: str, allowed_extensions: list[str]) -> bool:
    """Validate file extension"""
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in allowed_extensions

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    # Remove potentially dangerous characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return filename