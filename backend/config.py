from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Sentinel AI Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 2
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/database/sentinel.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Storage
    DATA_DIR: str = "./data"
    MODELS_DIR: str = "./data/models"
    UPLOADS_DIR: str = "./data/uploads"
    VIDEOS_DIR: str = "./data/videos"
    FACES_DIR: str = "./data/synthetic_faces"
    
    # ML Models
    FACE_DETECTION_CONFIDENCE: float = 0.7
    FACE_RECOGNITION_THRESHOLD: float = 0.6
    BEHAVIOR_ANOMALY_THRESHOLD: float = 0.75
    DEEPFAKE_THRESHOLD: float = 0.8
    LIVENESS_THRESHOLD: float = 0.7
    
    # Video Processing
    MAX_CAMERA_FEEDS: int = 4
    FRAME_RATE: int = 15
    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    VIDEO_BUFFER_SIZE: int = 30
    
    # Alerts
    ENABLE_VOICE_ALERTS: bool = True
    ENABLE_EMAIL_ALERTS: bool = False
    ALERT_COOLDOWN_SECONDS: int = 60
    
    # Federated Learning
    FEDERATED_ROUNDS: int = 5
    FEDERATED_MIN_NODES: int = 2
    FEDERATED_AGGREGATION_METHOD: str = "fedavg"
    
    # Performance
    MAX_WORKERS: int = 4
    BATCH_SIZE: int = 8
    USE_GPU: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/sentinel.log"
    
    # CORS - ADDED
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()