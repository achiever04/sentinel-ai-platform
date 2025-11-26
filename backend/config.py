# ============================================================================
# backend/config.py - COMPLETE Configuration with ALL Fields
# ============================================================================

from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # ============== APPLICATION SETTINGS ==============
    APP_NAME: str = "Sentinel AI Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # ============== SERVER CONFIGURATION ==============
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 2
    
    # ============== DATABASE ==============
    DATABASE_URL: str = "sqlite:///./data/database/sentinel.db"
    
    # ============== REDIS ==============
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""  # ADDED
    
    # ============== SECURITY ==============
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ============== STORAGE PATHS ==============
    DATA_DIR: str = "./data"
    MODELS_DIR: str = "./data/models"
    UPLOADS_DIR: str = "./data/uploads"
    VIDEOS_DIR: str = "./data/videos"
    FACES_DIR: str = "./data/synthetic_faces"
    LOGS_DIR: str = "./logs"  # ADDED
    
    # ============== ML MODEL CONFIGURATION ==============
    FACE_DETECTION_CONFIDENCE: float = 0.7
    FACE_RECOGNITION_THRESHOLD: float = 0.6
    FACE_DETECTION_MODEL: str = "hog"  # ADDED
    FACE_RECOGNITION_MODEL: str = "small"  # ADDED
    
    BEHAVIOR_ANOMALY_THRESHOLD: float = 0.75
    LOITERING_THRESHOLD_SECONDS: int = 60  # ADDED
    
    LIVENESS_THRESHOLD: float = 0.7
    DEEPFAKE_THRESHOLD: float = 0.8
    
    # ============== VIDEO PROCESSING ==============
    MAX_CAMERA_FEEDS: int = 4
    FRAME_RATE: int = 15
    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    VIDEO_BUFFER_SIZE: int = 30
    SKIP_FRAMES: int = 2  # ADDED
    
    # ============== ALERTS & NOTIFICATIONS ==============
    ENABLE_VOICE_ALERTS: bool = True
    ENABLE_EMAIL_ALERTS: bool = False
    ALERT_COOLDOWN_SECONDS: int = 60
    
    # Email Settings - ADDED
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = True
    SENDER_EMAIL: str = "your-email@gmail.com"
    SENDER_PASSWORD: str = "your-app-password"
    ALERT_RECIPIENT_EMAIL: str = "operator@sentinel.ai"
    
    # ============== FEDERATED LEARNING ==============
    FEDERATED_ROUNDS: int = 5
    FEDERATED_MIN_NODES: int = 2
    FEDERATED_AGGREGATION_METHOD: str = "fedavg"
    
    # ============== PERFORMANCE ==============
    MAX_WORKERS: int = 4
    BATCH_SIZE: int = 8
    USE_GPU: bool = False
    
    # ============== LOGGING ==============
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/sentinel.log"
    LOG_MAX_BYTES: int = 10485760  # ADDED
    LOG_BACKUP_COUNT: int = 5  # ADDED
    
    # ============== CORS ==============
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # ============== CELERY ==============
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"  # ADDED
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"  # ADDED
    
    # ============== FILE UPLOAD LIMITS ==============
    MAX_UPLOAD_SIZE_MB: int = 50  # ADDED
    ALLOWED_IMAGE_EXTENSIONS: str = "jpg,jpeg,png,bmp"  # ADDED
    ALLOWED_VIDEO_EXTENSIONS: str = "mp4,avi,mov,mkv"  # ADDED
    
    # ============== RATE LIMITING ==============
    RATE_LIMIT_ENABLED: bool = True  # ADDED
    RATE_LIMIT_PER_MINUTE: int = 60  # ADDED
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # IMPORTANT: Allow extra fields from .env that aren't defined here
        extra = "ignore"  # This prevents the validation error

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()