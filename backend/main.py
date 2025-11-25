from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.database import init_db
from backend.config import get_settings
from backend.utils.logger import setup_logger

# Import ALL API routers
from backend.api import auth, cameras, persons, watchlist, alerts, analytics, federated, uploads

settings = get_settings()
logger = setup_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Multi-Camera Safety & Intelligence Platform (Academic Use Only)"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    logger.info("Database initialized")
    logger.info("Application started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application")
    from backend.services.camera_service import CameraService
    for camera_id in list(CameraService.active_streams.keys()):
        CameraService.stop_stream(camera_id)

# Include ALL routers
app.include_router(auth.router)
app.include_router(cameras.router)
app.include_router(persons.router)
app.include_router(watchlist.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(federated.router)
app.include_router(uploads.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "ethical_notice": "This system uses SYNTHETIC DATA ONLY for academic purposes."
    }
